"""Tests for the client-organizations API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from tests.factories import (
    create_client as factory_create_client,
    create_client_organization,
)


@pytest.mark.asyncio
async def test_create_client_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """POST /api/v1/client-organizations creates a client organization."""
    resp = await client.post(
        "/api/v1/client-organizations",
        json={
            "name": "Acme AB",
            "org_number": "556111-2222",
            "industry": "Tech",
            "collective_agreement": "ITP1",
            "contact_person": "Sven Svensson",
            "contact_email": "sven@acme.se",
            "employee_count": 50,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme AB"
    assert data["org_number"] == "556111-2222"
    assert data["collective_agreement"] == "ITP1"
    assert data["employee_count"] == 50
    assert data["created_by"] == str(test_user.id)


@pytest.mark.asyncio
async def test_list_client_organizations(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/client-organizations returns org-scoped list."""
    await create_client_organization(
        db_session, test_org.id, test_user.id, name="Org A"
    )
    await create_client_organization(
        db_session, test_org.id, test_user.id, name="Org B"
    )

    resp = await client.get("/api/v1/client-organizations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    names = {o["name"] for o in data}
    assert "Org A" in names
    assert "Org B" in names


@pytest.mark.asyncio
async def test_list_includes_client_count(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/client-organizations includes client_count per org."""
    co = await create_client_organization(
        db_session, test_org.id, test_user.id, name="Counted Org"
    )
    await factory_create_client(
        db_session, test_org.id, test_user.id,
        name="Client A", client_organization_id=co.id,
    )
    await factory_create_client(
        db_session, test_org.id, test_user.id,
        name="Client B", client_organization_id=co.id,
    )

    resp = await client.get("/api/v1/client-organizations")
    assert resp.status_code == 200
    data = resp.json()
    matched = [o for o in data if o["name"] == "Counted Org"]
    assert len(matched) == 1
    assert matched[0]["client_count"] == 2


@pytest.mark.asyncio
async def test_get_client_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/client-organizations/{id} returns the detail view with clients."""
    co = await create_client_organization(
        db_session, test_org.id, test_user.id, name="Detail Org"
    )
    cl = await factory_create_client(
        db_session, test_org.id, test_user.id,
        name="Linked Client", client_organization_id=co.id,
    )

    resp = await client.get(f"/api/v1/client-organizations/{co.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Detail Org"
    assert data["client_count"] == 1
    assert len(data["clients"]) == 1
    assert data["clients"][0]["id"] == str(cl.id)


@pytest.mark.asyncio
async def test_get_client_organization_not_found(client: AsyncClient):
    """GET /api/v1/client-organizations/{nonexistent} returns 404."""
    resp = await client.get(f"/api/v1/client-organizations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_client_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/client-organizations/{id} updates fields."""
    co = await create_client_organization(
        db_session, test_org.id, test_user.id
    )

    resp = await client.patch(
        f"/api/v1/client-organizations/{co.id}",
        json={"name": "Uppdaterat Namn", "industry": "Finans"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Uppdaterat Namn"
    assert data["industry"] == "Finans"


@pytest.mark.asyncio
async def test_delete_client_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """DELETE /api/v1/client-organizations/{id} succeeds when no clients linked."""
    co = await create_client_organization(
        db_session, test_org.id, test_user.id
    )

    resp = await client.delete(f"/api/v1/client-organizations/{co.id}")
    assert resp.status_code == 204

    # Confirm it's gone
    resp = await client.get(f"/api/v1/client-organizations/{co.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_blocked_when_clients_linked(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """DELETE /api/v1/client-organizations/{id} returns 409 when clients exist."""
    co = await create_client_organization(
        db_session, test_org.id, test_user.id
    )
    await factory_create_client(
        db_session, test_org.id, test_user.id,
        client_organization_id=co.id,
    )

    resp = await client.delete(f"/api/v1/client-organizations/{co.id}")
    assert resp.status_code == 409
    assert "client(s) still linked" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_org_isolation_client_organizations(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
    second_org: Organization,
    second_user: User,
):
    """Org2 cannot see org1's client organizations."""
    co1 = await create_client_organization(
        db_session, test_org.id, test_user.id, name="Org1 Company"
    )
    co2 = await create_client_organization(
        db_session, second_org.id, second_user.id, name="Org2 Company"
    )

    # Org1 sees only their own
    resp1 = await client.get("/api/v1/client-organizations")
    ids1 = {o["id"] for o in resp1.json()}
    assert str(co1.id) in ids1
    assert str(co2.id) not in ids1

    # Org2 sees only their own
    resp2 = await client_org2.get("/api/v1/client-organizations")
    ids2 = {o["id"] for o in resp2.json()}
    assert str(co2.id) in ids2
    assert str(co1.id) not in ids2

    # Org2 cannot access org1's by ID
    resp = await client_org2.get(f"/api/v1/client-organizations/{co1.id}")
    assert resp.status_code == 404
