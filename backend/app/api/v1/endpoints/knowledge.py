import logging
from datetime import datetime, timezone
from uuid import UUID

import pdfplumber
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.audit_entry import AuditEntry
from app.models.base import AuditAction, ActorType, KnowledgeCategory
from app.models.knowledge_item import KnowledgeItem
from app.rate_limit import limiter
from app.schemas.knowledge_item import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemResponse,
    KnowledgeItemSearch,
)
from app.services.chunker import ChunkerService
from app.services.memory import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=KnowledgeItemResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_item(
    item_in: KnowledgeItemCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> KnowledgeItem:
    memory_service = MemoryService(db)
    item = await memory_service.create_knowledge_item(
        organization_id=organization_id,
        created_by=current_user.id,
        **item_in.model_dump(),
    )
    return item


@router.get("", response_model=list[KnowledgeItemResponse])
async def list_knowledge_items(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    skip: int = 0,
    limit: int = 100,
) -> list[KnowledgeItem]:
    result = await db.execute(
        select(KnowledgeItem)
        .where(
            KnowledgeItem.organization_id == organization_id,
            KnowledgeItem.is_active.is_(True),
        )
        .order_by(KnowledgeItem.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(
    item_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> KnowledgeItem:
    result = await db.execute(
        select(KnowledgeItem).where(
            KnowledgeItem.id == item_id,
            KnowledgeItem.organization_id == organization_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found"
        )
    return item


@router.patch("/{item_id}", response_model=KnowledgeItemResponse)
async def update_knowledge_item(
    item_id: UUID,
    item_in: KnowledgeItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> KnowledgeItem:
    result = await db.execute(
        select(KnowledgeItem).where(
            KnowledgeItem.id == item_id,
            KnowledgeItem.organization_id == organization_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found"
        )

    update_data = item_in.model_dump(exclude_unset=True)

    # If content changed, regenerate embedding
    content_changed = "content" in update_data and update_data["content"] != item.content

    for field, value in update_data.items():
        setattr(item, field, value)

    if content_changed:
        memory_service = MemoryService(db)
        item.embedding = await memory_service.generate_embedding(item.content)

    await db.flush()
    await db.refresh(item)
    return item


@router.post("/search", response_model=list[KnowledgeItemResponse])
async def search_knowledge(
    search: KnowledgeItemSearch,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[KnowledgeItem]:
    memory_service = MemoryService(db)
    items = await memory_service.search(
        organization_id=organization_id,
        query=search.query,
        category=search.category,
        tags=search.tags,
        limit=search.limit,
    )
    return items


@router.post("/ingest-document", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def ingest_knowledge_document(
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    file: UploadFile = File(...),
    category: str = Form(...),
    source: str = Form(...),
    tags: str = Form(""),
) -> dict:
    """Upload a PDF, extract text, chunk, embed, and store as knowledge items."""
    # Validate category
    try:
        knowledge_category = KnowledgeCategory(category)
    except ValueError:
        valid = [c.value for c in KnowledgeCategory]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{category}'. Valid: {valid}",
        )

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    # Extract text from PDF
    try:
        content = await file.read()
        import io

        text_parts: list[str] = []
        page_map: list[tuple[int, int, int]] = []  # (page_num, start_char, end_char)

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    start = sum(len(p) + 1 for p in text_parts)
                    text_parts.append(page_text)
                    page_map.append((page_num, start, start + len(page_text)))

        full_text = "\n\n".join(text_parts)
    except Exception as e:
        logger.error("PDF extraction failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to extract text from PDF: {e}",
        )

    if not full_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PDF contains no extractable text.",
        )

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # Chunk the document
    chunker = ChunkerService()
    chunks = chunker.chunk_document(
        text=full_text,
        source_title=source,
        metadata={"filename": file.filename},
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document produced no chunks after processing.",
        )

    # Generate embeddings in batch
    memory_service = MemoryService(db)
    chunk_texts = [c.content for c in chunks]
    embeddings = await memory_service.generate_embeddings_batch(chunk_texts)

    # Create knowledge items
    created_items: list[dict] = []
    for chunk, embedding in zip(chunks, embeddings):
        # Build title from section heading or chunk index
        if chunk.section_heading:
            title = f"{source} — {chunk.section_heading}"
        else:
            title = f"{source} — Chunk {chunk.chunk_index + 1}"

        # Auto-add section heading as a tag
        chunk_tags = list(tag_list)
        if chunk.section_heading:
            heading_tag = chunk.section_heading.strip().lower()[:50]
            if heading_tag not in chunk_tags:
                chunk_tags.append(heading_tag)

        # Resolve page number from character offset
        chunk_page: int | None = None
        if chunk.source_location and page_map:
            start = chunk.source_location.get("start_char", 0)
            for p_num, p_start, p_end in page_map:
                if p_start <= start < p_end:
                    chunk_page = p_num
                    break

        source_loc = {
            **chunk.source_location,
            "page_number": chunk_page,
        } if chunk.source_location else None

        item = await memory_service.create_knowledge_item(
            organization_id=organization_id,
            created_by=current_user.id,
            title=title,
            content=chunk.content,
            category=knowledge_category,
            source=source,
            tags=chunk_tags,
            embedding=embedding,
            source_location=source_loc,
        )
        created_items.append({
            "id": str(item.id),
            "title": title,
            "content_preview": chunk.content[:200],
        })

    # Create audit entry
    audit = AuditEntry(
        case_id=None,
        action=AuditAction.KNOWLEDGE_INGESTED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "filename": file.filename,
            "source": source,
            "category": category,
            "items_created": len(created_items),
        },
    )
    db.add(audit)
    await db.flush()

    logger.info(
        "Knowledge ingestion: %d items created from '%s' by user %s",
        len(created_items), file.filename, current_user.id,
    )

    return {
        "items_created": len(created_items),
        "chunks": created_items,
    }


@router.post("/re-embed")
async def re_embed_knowledge(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> dict:
    """Re-generate embeddings for all knowledge items using the current provider.

    Use this after switching embedding providers (e.g., OpenAI -> Voyage AI).
    """
    result = await db.execute(
        select(KnowledgeItem).where(
            KnowledgeItem.organization_id == organization_id,
            KnowledgeItem.is_active.is_(True),
        )
    )
    items = list(result.scalars().all())

    if not items:
        return {"re_embedded": 0}

    memory_service = MemoryService(db)

    # Process in batches of 50
    batch_size = 50
    total = 0
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        texts = [item.content for item in batch]
        embeddings = await memory_service.generate_embeddings_batch(texts)
        for item, embedding in zip(batch, embeddings):
            item.embedding = embedding
        total += len(batch)
        await db.flush()

    logger.info(
        "Re-embedded %d knowledge items for org %s",
        total, organization_id,
    )

    return {"re_embedded": total}
