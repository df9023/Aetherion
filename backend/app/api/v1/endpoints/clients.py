from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

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
        select(Client).where(
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
