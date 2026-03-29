"""Tests for the cases API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from tests.factories import create_client, create_case


@pytest.mark.asyncio
async def test_create_case(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """POST /api/v1/cases creates a case and returns 201."""
    test_client = await create_client(db_session, test_org.id, test_user.id)

    resp = await client.post(
        "/api/v1/cases",
        json={
            "client_id": str(test_client.id),
            "assigned_to": str(test_user.id),
            "title": "Ny pensionsöversyn",
            "case_type": "pension_review",
            "summary": "Test case",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Ny pensionsöversyn"
    assert data["case_type"] == "pension_review"
    assert data["status"] == "draft"
    assert data["organization_id"] == str(test_org.id)


@pytest.mark.asyncio
async def test_list_cases(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/cases returns list scoped to the user's org."""
    test_client = await create_client(db_session, test_org.id, test_user.id)
    await create_case(db_session, test_org.id, test_client.id, test_user.id, title="Case A")
    await create_case(db_session, test_org.id, test_client.id, test_user.id, title="Case B")

    resp = await client.get("/api/v1/cases")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    titles = {c["title"] for c in data}
    assert "Case A" in titles
    assert "Case B" in titles


@pytest.mark.asyncio
async def test_get_case(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/cases/{id} returns the case."""
    test_client = await create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_client.id, test_user.id)

    resp = await client.get(f"/api/v1/cases/{case.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(case.id)
    assert data["title"] == case.title


@pytest.mark.asyncio
async def test_get_case_not_found(client: AsyncClient):
    """GET /api/v1/cases/{nonexistent_id} returns 404."""
    resp = await client.get(f"/api/v1/cases/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_case_status(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/cases/{id} updates the status."""
    test_client = await create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_client.id, test_user.id)

    resp = await client.patch(
        f"/api/v1/cases/{case.id}",
        json={"status": "in_preparation"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "in_preparation"


@pytest.mark.asyncio
async def test_update_case_title(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/cases/{id} can update the title."""
    test_client = await create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_client.id, test_user.id)

    resp = await client.patch(
        f"/api/v1/cases/{case.id}",
        json={"title": "Uppdaterad titel"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Uppdaterad titel"


@pytest.mark.asyncio
async def test_update_case_not_found(client: AsyncClient):
    """PATCH /api/v1/cases/{nonexistent} returns 404."""
    resp = await client.patch(
        f"/api/v1/cases/{uuid.uuid4()}",
        json={"title": "Nope"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_isolation_cases(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Org2 client cannot see org1's cases."""
    test_client = await create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_client.id, test_user.id, title="Org1 only")

    # Org2 user lists cases — should not see org1's case
    resp = await client_org2.get("/api/v1/cases")
    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json()}
    assert str(case.id) not in ids

    # Org2 user fetches org1's case by ID — should get 404
    resp = await client_org2.get(f"/api/v1/cases/{case.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_case_audit_trail(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Creating a case should produce an audit entry, retrievable via GET /audit."""
    test_client = await create_client(db_session, test_org.id, test_user.id)

    # Create via API (which auto-creates audit entry)
    resp = await client.post(
        "/api/v1/cases",
        json={
            "client_id": str(test_client.id),
            "assigned_to": str(test_user.id),
            "title": "Audit test case",
            "case_type": "pension_review",
        },
    )
    assert resp.status_code == 201
    case_id = resp.json()["id"]

    # Fetch audit trail
    resp = await client.get(f"/api/v1/cases/{case_id}/audit")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) >= 1
    assert entries[0]["action"] == "case_created"
