"""Tests for firm insights API endpoints.

Covers CRUD, relevance matching (case_type / collective_agreement / client_org),
org isolation, upvote, and delete authorization.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.base import (
    AuditAction,
    CaseType,
    CollectiveAgreement,
    UserRole,
)
from app.models.audit_entry import AuditEntry
from sqlalchemy import select
from tests.factories import (
    create_case,
    create_client,
    create_client_organization,
)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_firm_insight(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    resp = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "McKinsey HR kräver 3 månaders varsel",
            "content": "Vid löneväxling måste McKinsey HR notifieras 3 månader innan.",
            "category": "client_specific",
            "case_types": ["salary_exchange"],
            "collective_agreements": ["ITP1"],
            "tags": ["mckinsey", "varsel"],
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "McKinsey HR kräver 3 månaders varsel"
    assert data["category"] == "client_specific"
    assert data["case_types"] == ["salary_exchange"]
    assert data["collective_agreements"] == ["ITP1"]
    assert data["organization_id"] == str(test_org.id)
    assert data["created_by"] == str(test_user.id)
    assert data["upvotes"] == 0
    assert data["is_active"] is True

    # Audit entry created
    result = await db_session.execute(
        select(AuditEntry).where(AuditEntry.action == AuditAction.INSIGHT_CREATED)
    )
    entries = list(result.scalars().all())
    assert len(entries) == 1
    assert entries[0].details["insight_id"] == data["id"]


@pytest.mark.asyncio
async def test_list_firm_insights(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    await client.post(
        "/api/v1/firm-insights",
        json={"title": "A", "content": "Content A", "category": "general"},
    )
    await client.post(
        "/api/v1/firm-insights",
        json={"title": "B", "content": "Content B", "category": "product_tip"},
    )

    resp = await client.get("/api/v1/firm-insights")
    assert resp.status_code == 200
    data = resp.json()
    titles = {i["title"] for i in data}
    assert {"A", "B"}.issubset(titles)


@pytest.mark.asyncio
async def test_list_firm_insights_filter_by_category(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    await client.post(
        "/api/v1/firm-insights",
        json={"title": "Gen", "content": "g", "category": "general"},
    )
    await client.post(
        "/api/v1/firm-insights",
        json={"title": "Tip", "content": "t", "category": "product_tip"},
    )

    resp = await client.get("/api/v1/firm-insights?category=product_tip")
    assert resp.status_code == 200
    data = resp.json()
    assert all(i["category"] == "product_tip" for i in data)
    assert "Tip" in {i["title"] for i in data}
    assert "Gen" not in {i["title"] for i in data}


@pytest.mark.asyncio
async def test_list_firm_insights_filter_by_case_type(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "SX",
            "content": "salary exchange",
            "category": "process_note",
            "case_types": ["salary_exchange"],
        },
    )
    await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "PR",
            "content": "pension review",
            "category": "process_note",
            "case_types": ["pension_review"],
        },
    )

    resp = await client.get("/api/v1/firm-insights?case_type=salary_exchange")
    assert resp.status_code == 200
    titles = {i["title"] for i in resp.json()}
    assert "SX" in titles
    assert "PR" not in titles


@pytest.mark.asyncio
async def test_list_firm_insights_search(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Löneväxlingstips",
            "content": "Tänk på taket",
            "category": "general",
        },
    )
    await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Annat",
            "content": "Helt orelaterat",
            "category": "general",
        },
    )

    resp = await client.get("/api/v1/firm-insights?search=löneväxling")
    assert resp.status_code == 200
    titles = {i["title"] for i in resp.json()}
    assert "Löneväxlingstips" in titles
    assert "Annat" not in titles


@pytest.mark.asyncio
async def test_get_firm_insight(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "X", "content": "x content", "category": "general"},
    )
    insight_id = create.json()["id"]

    resp = await client.get(f"/api/v1/firm-insights/{insight_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == insight_id


@pytest.mark.asyncio
async def test_get_firm_insight_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/firm-insights/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_firm_insight(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Old", "content": "old content", "category": "general"},
    )
    insight_id = create.json()["id"]

    resp = await client.patch(
        f"/api/v1/firm-insights/{insight_id}",
        json={"title": "New", "tags": ["uppdaterad"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New"
    assert data["tags"] == ["uppdaterad"]


@pytest.mark.asyncio
async def test_delete_firm_insight_as_creator(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Gone", "content": "x", "category": "general"},
    )
    insight_id = create.json()["id"]

    resp = await client.delete(f"/api/v1/firm-insights/{insight_id}")
    assert resp.status_code == 204

    # Confirm gone
    get_resp = await client.get(f"/api/v1/firm-insights/{insight_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_firm_insight_forbidden_for_non_creator(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Another user in the same org who is not admin cannot delete."""
    # Create insight as test_user
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Mine", "content": "x", "category": "general"},
    )
    insight_id = create.json()["id"]

    # Create a second advisor in the same org
    other = User(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        email=f"other-{uuid.uuid4().hex[:8]}@testorg.se",
        name="Annan Rådgivare",
        role=UserRole.ADVISOR,
        is_active=True,
    )
    db_session.add(other)
    await db_session.commit()

    from httpx import ASGITransport, AsyncClient as _AC
    from app.main import app

    async with _AC(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-Dev-User-Id": str(other.id)},
    ) as other_client:
        resp = await other_client.delete(f"/api/v1/firm-insights/{insight_id}")
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_firm_insight_as_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """An admin in the same org can delete another user's insight."""
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Admin kan radera", "content": "x", "category": "general"},
    )
    insight_id = create.json()["id"]

    admin = User(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        email=f"admin-{uuid.uuid4().hex[:8]}@testorg.se",
        name="Admin Adminsson",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    from httpx import ASGITransport, AsyncClient as _AC
    from app.main import app

    async with _AC(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-Dev-User-Id": str(admin.id)},
    ) as admin_client:
        resp = await admin_client.delete(f"/api/v1/firm-insights/{insight_id}")
        assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Upvote
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upvote_firm_insight(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Uppröstad", "content": "x", "category": "general"},
    )
    insight_id = create.json()["id"]

    resp = await client.post(f"/api/v1/firm-insights/{insight_id}/upvote")
    assert resp.status_code == 200
    assert resp.json()["upvotes"] == 1

    # Second upvote from same user is idempotent
    resp2 = await client.post(f"/api/v1/firm-insights/{insight_id}/upvote")
    assert resp2.status_code == 200
    assert resp2.json()["upvotes"] == 1


@pytest.mark.asyncio
async def test_upvote_increments_for_different_users(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Flera röster", "content": "x", "category": "general"},
    )
    insight_id = create.json()["id"]

    # First upvote from test_user
    resp = await client.post(f"/api/v1/firm-insights/{insight_id}/upvote")
    assert resp.json()["upvotes"] == 1

    # Second user (same org)
    other = User(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        email=f"v2-{uuid.uuid4().hex[:8]}@testorg.se",
        name="Röst Två",
        role=UserRole.ADVISOR,
        is_active=True,
    )
    db_session.add(other)
    await db_session.commit()

    from httpx import ASGITransport, AsyncClient as _AC
    from app.main import app

    async with _AC(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-Dev-User-Id": str(other.id)},
    ) as other_client:
        resp2 = await other_client.post(f"/api/v1/firm-insights/{insight_id}/upvote")
        assert resp2.status_code == 200
        assert resp2.json()["upvotes"] == 2


# ---------------------------------------------------------------------------
# Org isolation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_org_isolation_firm_insights(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    create = await client.post(
        "/api/v1/firm-insights",
        json={"title": "Org1 Insight", "content": "x", "category": "general"},
    )
    insight_id = create.json()["id"]

    # Org2 cannot list
    resp = await client_org2.get("/api/v1/firm-insights")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert insight_id not in ids

    # Org2 cannot fetch
    resp = await client_org2.get(f"/api/v1/firm-insights/{insight_id}")
    assert resp.status_code == 404

    # Org2 cannot delete
    resp = await client_org2.delete(f"/api/v1/firm-insights/{insight_id}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Relevance matching
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_relevant_matches_on_case_type(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Insights matching the case's case_type are returned; unrelated are not."""
    test_client = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    case = await create_case(
        db_session, test_org.id, test_client.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
    )

    # Match: salary_exchange
    match = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Match SX",
            "content": "x",
            "category": "process_note",
            "case_types": ["salary_exchange"],
        },
    )
    match_id = match.json()["id"]

    # Not match: transfer_advice
    other = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Unrelated",
            "content": "x",
            "category": "process_note",
            "case_types": ["transfer_advice"],
        },
    )
    other_id = other.json()["id"]

    resp = await client.get(f"/api/v1/firm-insights/relevant?case_id={case.id}")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert match_id in ids
    assert other_id not in ids


@pytest.mark.asyncio
async def test_relevant_matches_on_collective_agreement(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    test_client = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    case = await create_case(
        db_session, test_org.id, test_client.id, test_user.id,
        case_type=CaseType.PENSION_REVIEW,
    )

    match = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "ITP1 quirk",
            "content": "x",
            "category": "product_tip",
            "collective_agreements": ["ITP1"],
        },
    )
    other = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "SAF-LO quirk",
            "content": "x",
            "category": "product_tip",
            "collective_agreements": ["SAF_LO"],
        },
    )

    resp = await client.get(f"/api/v1/firm-insights/relevant?case_id={case.id}")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert match.json()["id"] in ids
    assert other.json()["id"] not in ids


@pytest.mark.asyncio
async def test_relevant_matches_on_client_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_org = await create_client_organization(
        db_session, test_org.id, test_user.id, name="Volvo AB"
    )
    test_client = await create_client(
        db_session, test_org.id, test_user.id,
        client_organization_id=client_org.id,
    )
    case = await create_case(
        db_session, test_org.id, test_client.id, test_user.id,
        case_type=CaseType.OTHER,
    )

    match = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Volvo-specifikt",
            "content": "x",
            "category": "client_specific",
            "client_organization_id": str(client_org.id),
        },
    )

    other_co = await create_client_organization(
        db_session, test_org.id, test_user.id, name="Skanska AB",
    )
    other = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Skanska-specifikt",
            "content": "x",
            "category": "client_specific",
            "client_organization_id": str(other_co.id),
        },
    )

    resp = await client.get(f"/api/v1/firm-insights/relevant?case_id={case.id}")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert match.json()["id"] in ids
    assert other.json()["id"] not in ids


@pytest.mark.asyncio
async def test_relevant_ranks_by_specificity(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Insights matching more scoping fields rank higher."""
    client_org = await create_client_organization(
        db_session, test_org.id, test_user.id, name="Ericsson"
    )
    test_client = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
        client_organization_id=client_org.id,
    )
    case = await create_case(
        db_session, test_org.id, test_client.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
    )

    # Specificity 1: only case_type matches
    low = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Low spec",
            "content": "x",
            "category": "process_note",
            "case_types": ["salary_exchange"],
        },
    )

    # Specificity 3: case_type + agreement + client_org all match
    high = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "High spec",
            "content": "x",
            "category": "client_specific",
            "case_types": ["salary_exchange"],
            "collective_agreements": ["ITP1"],
            "client_organization_id": str(client_org.id),
        },
    )

    resp = await client.get(f"/api/v1/firm-insights/relevant?case_id={case.id}")
    assert resp.status_code == 200
    results = resp.json()
    result_ids = [i["id"] for i in results]
    assert high.json()["id"] in result_ids
    assert low.json()["id"] in result_ids
    # High specificity must come first
    assert result_ids.index(high.json()["id"]) < result_ids.index(low.json()["id"])


@pytest.mark.asyncio
async def test_relevant_excludes_inactive(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    test_client = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    case = await create_case(
        db_session, test_org.id, test_client.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
    )

    create = await client.post(
        "/api/v1/firm-insights",
        json={
            "title": "Inaktiv",
            "content": "x",
            "category": "general",
            "case_types": ["salary_exchange"],
        },
    )
    insight_id = create.json()["id"]

    # Deactivate
    await client.patch(
        f"/api/v1/firm-insights/{insight_id}",
        json={"is_active": False},
    )

    resp = await client.get(f"/api/v1/firm-insights/relevant?case_id={case.id}")
    assert resp.status_code == 200
    ids = {i["id"] for i in resp.json()}
    assert insight_id not in ids


@pytest.mark.asyncio
async def test_relevant_case_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/firm-insights/relevant?case_id={uuid.uuid4()}")
    assert resp.status_code == 404
