"""Tests for the knowledge API endpoints.

Note: The POST /knowledge endpoint uses MemoryService.create_knowledge_item()
which generates embeddings. We test the simpler CRUD paths and skip the
embedding-dependent search endpoint.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from tests.factories import create_knowledge_item


@pytest.mark.asyncio
async def test_list_knowledge_items(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/knowledge returns org-scoped list."""
    await create_knowledge_item(
        db_session, test_org.id, test_user.id, title="Item A"
    )
    await create_knowledge_item(
        db_session, test_org.id, test_user.id, title="Item B"
    )

    resp = await client.get("/api/v1/knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    titles = {item["title"] for item in data}
    assert "Item A" in titles
    assert "Item B" in titles


@pytest.mark.asyncio
async def test_get_knowledge_item(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/knowledge/{id} returns the item."""
    item = await create_knowledge_item(db_session, test_org.id, test_user.id)

    resp = await client.get(f"/api/v1/knowledge/{item.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(item.id)
    assert data["title"] == item.title


@pytest.mark.asyncio
async def test_get_knowledge_item_not_found(client: AsyncClient):
    """GET /api/v1/knowledge/{nonexistent} returns 404."""
    resp = await client.get(f"/api/v1/knowledge/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_isolation_knowledge(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Org2 cannot see org1's knowledge items."""
    item = await create_knowledge_item(
        db_session, test_org.id, test_user.id, title="Org1 Knowledge"
    )

    # Org2 lists — should not include org1's item
    resp = await client_org2.get("/api/v1/knowledge")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert str(item.id) not in ids

    # Org2 fetches by ID — 404
    resp = await client_org2.get(f"/api/v1/knowledge/{item.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_knowledge_item(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/knowledge/{id} updates fields."""
    item = await create_knowledge_item(db_session, test_org.id, test_user.id)

    resp = await client.patch(
        f"/api/v1/knowledge/{item.id}",
        json={"title": "Uppdaterad titel"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Uppdaterad titel"


@pytest.mark.asyncio
async def test_deactivate_knowledge_item(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/knowledge/{id} can deactivate an item."""
    item = await create_knowledge_item(db_session, test_org.id, test_user.id)

    resp = await client.patch(
        f"/api/v1/knowledge/{item.id}",
        json={"is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    # Deactivated item should not appear in list (which filters is_active=True)
    resp = await client.get("/api/v1/knowledge")
    ids = {i["id"] for i in resp.json()}
    assert str(item.id) not in ids
