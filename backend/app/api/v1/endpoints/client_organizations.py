import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.client import Client
from app.models.client_organization import ClientOrganization
from app.schemas.client_organization import (
    ClientOrganizationCreate,
    ClientOrganizationUpdate,
    ClientOrganizationResponse,
    ClientOrganizationDetail,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ClientOrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_client_organization(
    co_in: ClientOrganizationCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> ClientOrganization:
    co = ClientOrganization(
        **co_in.model_dump(),
        organization_id=organization_id,
        created_by=current_user.id,
    )
    db.add(co)
    await db.flush()
    await db.refresh(co)
    return co


@router.get("", response_model=list[ClientOrganizationResponse])
async def list_client_organizations(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[ClientOrganizationResponse]:
    # Query client organizations with client count via subquery
    client_count_sq = (
        select(
            Client.client_organization_id,
            func.count(Client.id).label("cnt"),
        )
        .where(Client.client_organization_id.isnot(None))
        .group_by(Client.client_organization_id)
        .subquery()
    )

    result = await db.execute(
        select(ClientOrganization)
        .where(ClientOrganization.organization_id == organization_id)
        .order_by(ClientOrganization.name.asc())
    )
    orgs = list(result.scalars().all())

    # Fetch counts
    count_result = await db.execute(
        select(client_count_sq.c.client_organization_id, client_count_sq.c.cnt)
    )
    count_map = {row[0]: row[1] for row in count_result}

    responses = []
    for org in orgs:
        resp = ClientOrganizationResponse.model_validate(org)
        resp.client_count = count_map.get(org.id, 0)
        responses.append(resp)

    return responses


@router.get("/{co_id}", response_model=ClientOrganizationDetail)
async def get_client_organization(
    co_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> ClientOrganizationDetail:
    result = await db.execute(
        select(ClientOrganization)
        .options(selectinload(ClientOrganization.clients))
        .where(
            ClientOrganization.id == co_id,
            ClientOrganization.organization_id == organization_id,
        )
    )
    co = result.scalar_one_or_none()
    if not co:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client organization not found")

    resp = ClientOrganizationDetail.model_validate(co)
    resp.client_count = len(co.clients)
    return resp


@router.patch("/{co_id}", response_model=ClientOrganizationResponse)
async def update_client_organization(
    co_id: UUID,
    co_in: ClientOrganizationUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> ClientOrganization:
    result = await db.execute(
        select(ClientOrganization).where(
            ClientOrganization.id == co_id,
            ClientOrganization.organization_id == organization_id,
        )
    )
    co = result.scalar_one_or_none()
    if not co:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client organization not found")

    update_data = co_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(co, field, value)

    await db.flush()
    await db.refresh(co)
    return co


@router.delete("/{co_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_organization(
    co_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> None:
    result = await db.execute(
        select(ClientOrganization)
        .options(selectinload(ClientOrganization.clients))
        .where(
            ClientOrganization.id == co_id,
            ClientOrganization.organization_id == organization_id,
        )
    )
    co = result.scalar_one_or_none()
    if not co:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client organization not found")

    if co.clients:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete: {len(co.clients)} client(s) still linked",
        )

    await db.delete(co)
    await db.flush()
