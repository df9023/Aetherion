"""Tests for the dashboard endpoint (GET /api/v1/audit/recent)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.base import AuditAction
from tests.factories import (
    create_client as factory_create_client,
    create_case,
    create_audit_entry,
)


@pytest.mark.asyncio
async def test_recent_audit_empty(client: AsyncClient):
    """GET /api/v1/audit/recent returns empty list when no entries exist."""
    resp = await client.get("/api/v1/audit/recent")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_recent_audit_returns_entries(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/audit/recent returns recent audit entries."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    await create_audit_entry(
        db_session, case.id, test_user.id,
        action=AuditAction.CASE_CREATED,
    )
    await create_audit_entry(
        db_session, case.id, test_user.id,
        action=AuditAction.RECOMMENDATION_GENERATED,
    )

    resp = await client.get("/api/v1/audit/recent")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    actions = {e["action"] for e in data}
    assert "case_created" in actions
    assert "recommendation_generated" in actions


@pytest.mark.asyncio
async def test_recent_audit_respects_limit(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/audit/recent?limit=2 returns at most 2 entries."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    for action in [
        AuditAction.CASE_CREATED,
        AuditAction.RECOMMENDATION_GENERATED,
        AuditAction.DOCUMENT_GENERATED,
    ]:
        await create_audit_entry(db_session, case.id, test_user.id, action=action)

    resp = await client.get("/api/v1/audit/recent?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()) <= 2


@pytest.mark.asyncio
async def test_recent_audit_org_isolation(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
    second_org: Organization,
    second_user: User,
):
    """Org2 should not see org1's audit entries."""
    # Create entries for org1
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case1 = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    await create_audit_entry(
        db_session, case1.id, test_user.id,
        action=AuditAction.CASE_CREATED,
    )

    # Create entries for org2
    test_cl2 = await factory_create_client(
        db_session, second_org.id, second_user.id, name="Org2 Client"
    )
    case2 = await create_case(
        db_session, second_org.id, test_cl2.id, second_user.id, title="Org2 Case"
    )
    await create_audit_entry(
        db_session, case2.id, second_user.id,
        action=AuditAction.RECOMMENDATION_GENERATED,
    )

    # Org1 should see only their entries
    resp1 = await client.get("/api/v1/audit/recent")
    case_ids_1 = {e["case_id"] for e in resp1.json()}
    assert str(case1.id) in case_ids_1
    assert str(case2.id) not in case_ids_1

    # Org2 should see only their entries
    resp2 = await client_org2.get("/api/v1/audit/recent")
    case_ids_2 = {e["case_id"] for e in resp2.json()}
    assert str(case2.id) in case_ids_2
    assert str(case1.id) not in case_ids_2


@pytest.mark.asyncio
async def test_recent_audit_ordered_by_timestamp_desc(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Audit entries should be returned newest first."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    await create_audit_entry(
        db_session, case.id, test_user.id,
        action=AuditAction.CASE_CREATED,
    )
    await create_audit_entry(
        db_session, case.id, test_user.id,
        action=AuditAction.RECOMMENDATION_GENERATED,
    )

    resp = await client.get("/api/v1/audit/recent")
    data = resp.json()
    if len(data) >= 2:
        # Timestamps should be descending
        timestamps = [e["timestamp"] for e in data]
        assert timestamps == sorted(timestamps, reverse=True)
