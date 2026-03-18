from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.knowledge_item import KnowledgeItem
from app.schemas.knowledge_item import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemResponse,
    KnowledgeItemSearch,
)
from app.services.memory import MemoryService

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
            KnowledgeItem.is_active == True,
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
