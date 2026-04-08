"""Tests for the clients API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from tests.factories import create_client as factory_create_client


@pytest.mark.asyncio
async def test_create_client(
    client: AsyncClient,
    test_org: Organization,
    test_user: User,
):
    """POST /api/v1/clients creates a client and returns 201."""
    resp = await client.post(
        "/api/v1/clients",
        json={
            "name": "Karin Karlsson",
            "date_of_birth": "1975-03-20",
            "employment_status": "employed",
            "collective_agreement": "ITP1",
            "annual_income": "550000",
            "employer_name": "Acme AB",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Karin Karlsson"
    assert data["employment_status"] == "employed"
    assert data["collective_agreement"] == "ITP1"
    assert data["organization_id"] == str(test_org.id)
    assert data["created_by"] == str(test_user.id)


@pytest.mark.asyncio
async def test_list_clients(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/clients returns org-scoped list."""
    await factory_create_client(db_session, test_org.id, test_user.id, name="Client A")
    await factory_create_client(db_session, test_org.id, test_user.id, name="Client B")

    resp = await client.get("/api/v1/clients")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    names = {c["name"] for c in data}
    assert "Client A" in names
    assert "Client B" in names


@pytest.mark.asyncio
async def test_get_client(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/clients/{id} returns the client."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)

    resp = await client.get(f"/api/v1/clients/{test_cl.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(test_cl.id)


@pytest.mark.asyncio
async def test_get_client_not_found(client: AsyncClient):
    """GET /api/v1/clients/{nonexistent_id} returns 404."""
    resp = await client.get(f"/api/v1/clients/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_client(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/clients/{id} updates specified fields."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)

    resp = await client.patch(
        f"/api/v1/clients/{test_cl.id}",
        json={"employer_name": "New Corp AB", "annual_income": "700000"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["employer_name"] == "New Corp AB"
    assert float(data["annual_income"]) == 700000.0


@pytest.mark.asyncio
async def test_org_isolation_clients(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Org2 cannot see org1's clients."""
    test_cl = await factory_create_client(
        db_session, test_org.id, test_user.id, name="Org1 Client"
    )

    # Org2 lists clients — should not include org1's
    resp = await client_org2.get("/api/v1/clients")
    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json()}
    assert str(test_cl.id) not in ids

    # Org2 fetches org1's client by ID — 404
    resp = await client_org2.get(f"/api/v1/clients/{test_cl.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_client_missing_required_field(client: AsyncClient):
    """POST /api/v1/clients without required field returns 422."""
    resp = await client.post(
        "/api/v1/clients",
        json={
            "name": "Missing DOB",
            # date_of_birth is required but missing
            "employment_status": "employed",
            "collective_agreement": "ITP1",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_client_invalid_enum(client: AsyncClient):
    """POST /api/v1/clients with invalid enum value returns 422."""
    resp = await client.post(
        "/api/v1/clients",
        json={
            "name": "Invalid Enum",
            "date_of_birth": "1985-01-01",
            "employment_status": "invalid_status",
            "collective_agreement": "ITP1",
        },
    )
    assert resp.status_code == 422
