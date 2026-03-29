import logging
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.config import get_settings
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.rate_limit import limiter
from app.services.reasoner import ReasonerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Client:
    client = Client(
        **client_in.model_dump(),
        organization_id=organization_id,
        created_by=current_user.id,
    )
    db.add(client)
    await db.flush()
    await db.refresh(client)
    return client


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    skip: int = 0,
    limit: int = 100,
) -> list[Client]:
    result = await db.execute(
        select(Client)
        .options(selectinload(Client.client_organization))
        .where(Client.organization_id == organization_id)
        .order_by(Client.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Client:
    result = await db.execute(
        select(Client)
        .options(selectinload(Client.client_organization))
        .where(
            Client.id == client_id,
            Client.organization_id == organization_id,
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_in: ClientUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Client:
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == organization_id,
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    update_data = client_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    await db.flush()
    await db.refresh(client)
    return client


@router.post("/{client_id}/ingest-document")
@limiter.limit("10/minute")
async def ingest_document(
    request: Request,
    client_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    file: UploadFile = File(...),
) -> dict:
    """Upload a PDF and extract structured pension data using Claude.

    Returns the extraction result for advisor review — does NOT update the client.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ANTHROPIC_API_KEY not configured.",
        )

    # Verify client belongs to org
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == organization_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF files are supported.",
        )

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File too large. Maximum 20 MB.",
        )

    # Extract text from PDF
    import io
    import pdfplumber

    document_text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                document_text += text + "\n"

    if not document_text.strip():
        # Fall back to vision-only if no text could be extracted (scanned PDF)
        document_text = "(Skannat dokument — ingen text kunde extraheras. Analysera bilden.)"

    # Extract structured data via Claude
    reasoner = ReasonerService(db)
    extraction = await reasoner.extract_document_data(
        document_text=document_text,
        pdf_bytes=pdf_bytes,
    )

    return extraction


class ApplyExtractionRequest(BaseModel):
    """Fields confirmed by the advisor to apply to the client."""
    name: str | None = None
    date_of_birth: str | None = None
    employer_name: str | None = None
    collective_agreement: str | None = None
    annual_income: str | None = None
    employment_status: str | None = None
    desired_retirement_age: int | None = None
    risk_profile: str | None = None


@router.post("/{client_id}/apply-extraction", response_model=ClientResponse)
async def apply_extraction(
    client_id: UUID,
    body: ApplyExtractionRequest,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Client:
    """Apply advisor-confirmed extracted fields to a client profile."""
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == organization_id,
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    # Build update using the existing ClientUpdate schema for validation
    update_data = body.model_dump(exclude_unset=True)
    # Remove None values (fields the advisor didn't select)
    update_data = {k: v for k, v in update_data.items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields to apply.",
        )

    client_update = ClientUpdate(**update_data)
    validated = client_update.model_dump(exclude_unset=True)

    changed_fields = {}
    for field, value in validated.items():
        old_value = getattr(client, field)
        setattr(client, field, value)
        changed_fields[field] = {"old": str(old_value), "new": str(value)}

    logger.info(
        "Document extraction applied to client %s: %s",
        client_id,
        list(changed_fields.keys()),
    )

    await db.flush()
    await db.refresh(client)
    await db.commit()
    return client
