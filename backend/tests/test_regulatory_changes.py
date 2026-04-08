"""Tests for Regulatory Pulse: regulatory changes, scan, impacts, compliance health."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.audit_entry import AuditEntry
from app.models.base import (
    AuditAction,
    CaseImpactStatus,
    CaseStatus,
    CaseType,
    CollectiveAgreement,
)
from tests.factories import create_case, create_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _make_change(
    client: AsyncClient,
    *,
    title: str = "Test change",
    severity: str = "high",
    affected_case_types: list[str] | None = None,
    affected_agreements: list[str] | None = None,
) -> dict:
    resp = await client.post(
        "/api/v1/regulatory-changes",
        json={
            "title": title,
            "description": "A meaningful description of the change.",
            "source": "Finansinspektionen",
            "source_url": "https://fi.se/test",
            "severity": severity,
            "affected_case_types": affected_case_types or [],
            "affected_agreements": affected_agreements or [],
            "affected_tags": [],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_regulatory_change(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    resp = await client.post(
        "/api/v1/regulatory-changes",
        json={
            "title": "FFFS 2026:4 — Nya dokumentationskrav",
            "description": "Uppdaterade krav på dokumentation vid löneväxling.",
            "source": "Finansinspektionen",
            "source_url": "https://fi.se/fffs-2026-4",
            "severity": "high",
            "affected_case_types": ["salary_exchange"],
            "affected_agreements": ["ITP1"],
            "affected_tags": ["löneväxling"],
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "FFFS 2026:4 — Nya dokumentationskrav"
    assert data["severity"] == "high"
    assert data["affected_case_types"] == ["salary_exchange"]
    assert data["organization_id"] == str(test_org.id)
    assert data["created_by"] == str(test_user.id)
    assert data["is_active"] is True
    assert data["impact_count"] == 0
    assert data["open_impact_count"] == 0

    # Audit entry created
    result = await db_session.execute(
        select(AuditEntry).where(
            AuditEntry.action == AuditAction.REGULATORY_CHANGE_CREATED
        )
    )
    entries = list(result.scalars().all())
    assert len(entries) == 1
    assert entries[0].details["regulatory_change_id"] == data["id"]


@pytest.mark.asyncio
async def test_list_regulatory_changes(client: AsyncClient):
    await _make_change(client, title="A", severity="high")
    await _make_change(client, title="B", severity="medium")
    await _make_change(client, title="C", severity="low")

    resp = await client.get("/api/v1/regulatory-changes")
    assert resp.status_code == 200
    titles = {c["title"] for c in resp.json()}
    assert {"A", "B", "C"}.issubset(titles)

    # Filter by severity
    resp = await client.get("/api/v1/regulatory-changes?severity=high")
    assert resp.status_code == 200
    data = resp.json()
    assert all(c["severity"] == "high" for c in data)
    assert any(c["title"] == "A" for c in data)


@pytest.mark.asyncio
async def test_get_regulatory_change(client: AsyncClient):
    change = await _make_change(client, title="Lookup")
    resp = await client.get(f"/api/v1/regulatory-changes/{change['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Lookup"


@pytest.mark.asyncio
async def test_update_regulatory_change(client: AsyncClient):
    change = await _make_change(client, title="Old")
    resp = await client.patch(
        f"/api/v1/regulatory-changes/{change['id']}",
        json={"title": "New", "is_active": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_regulatory_change(client: AsyncClient):
    change = await _make_change(client, title="Bye")
    resp = await client.delete(f"/api/v1/regulatory-changes/{change['id']}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/regulatory-changes/{change['id']}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Scan logic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_scan_matches_by_case_type(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    # Active case matching case type
    case_match = await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.IN_PREPARATION,
        title="Salary exchange case",
    )
    # Active case with different case type
    case_miss = await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.PENSION_REVIEW,
        status=CaseStatus.IN_PREPARATION,
        title="Pension review",
    )
    # Archived case — should be skipped
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.ARCHIVED,
        title="Archived",
    )

    change = await _make_change(
        client,
        title="Salary exchange rule",
        affected_case_types=["salary_exchange"],
    )

    resp = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["new_impacts"] == 1
    assert data["total_matched_cases"] == 1
    assert data["skipped_existing"] == 0
    assert len(data["impacts"]) == 1
    assert data["impacts"][0]["case_id"] == str(case_match.id)
    assert data["impacts"][0]["status"] == "open"
    assert "case_type" in data["impacts"][0]["affected_sections"]

    # Audit entry created
    result = await db_session.execute(
        select(AuditEntry).where(
            AuditEntry.action == AuditAction.IMPACT_SCAN_COMPLETED
        )
    )
    entries = list(result.scalars().all())
    assert len(entries) == 1


@pytest.mark.asyncio
async def test_scan_matches_by_agreement(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    itp1_client = await create_client(
        db_session, test_org.id, test_user.id,
        name="ITP1 person",
        collective_agreement=CollectiveAgreement.ITP1,
    )
    saf_client = await create_client(
        db_session, test_org.id, test_user.id,
        name="SAF person",
        collective_agreement=CollectiveAgreement.SAF_LO,
    )
    await create_case(
        db_session, test_org.id, itp1_client.id, test_user.id,
        case_type=CaseType.PENSION_REVIEW,
        status=CaseStatus.DRAFT,
        title="ITP1 case",
    )
    await create_case(
        db_session, test_org.id, saf_client.id, test_user.id,
        case_type=CaseType.PENSION_REVIEW,
        status=CaseStatus.DRAFT,
        title="SAF case",
    )

    change = await _make_change(
        client, title="ITP1 only", affected_agreements=["ITP1"]
    )
    resp = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_impacts"] == 1
    impact = data["impacts"][0]
    assert "collective_agreement" in impact["affected_sections"]


@pytest.mark.asyncio
async def test_scan_skips_completed_cases(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.COMPLETED,
        title="Completed",
    )
    change = await _make_change(
        client, affected_case_types=["salary_exchange"]
    )
    resp = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    assert resp.status_code == 200
    assert resp.json()["new_impacts"] == 0


@pytest.mark.asyncio
async def test_scan_skips_duplicates(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="Case 1",
    )

    change = await _make_change(
        client, affected_case_types=["salary_exchange"]
    )

    # First scan creates the impact
    resp = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    assert resp.status_code == 200
    assert resp.json()["new_impacts"] == 1

    # Second scan should skip — no new impacts
    resp = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_impacts"] == 0
    assert data["skipped_existing"] == 1
    assert data["total_matched_cases"] == 1


# ---------------------------------------------------------------------------
# Resolve / acknowledge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_case_impact(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="Impact case",
    )
    change = await _make_change(
        client, affected_case_types=["salary_exchange"]
    )
    scan = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    impact_id = scan.json()["impacts"][0]["id"]

    resp = await client.patch(
        f"/api/v1/regulatory-changes/case-impacts/{impact_id}/resolve",
        json={"resolution_note": "Granskat, inga ändringar behövs."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "Granskat, inga ändringar behövs."
    assert data["resolved_by"] == str(test_user.id)
    assert data["resolved_at"] is not None


@pytest.mark.asyncio
async def test_acknowledge_case_impact(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="Ack case",
    )
    change = await _make_change(client, affected_case_types=["salary_exchange"])
    scan = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    impact_id = scan.json()["impacts"][0]["id"]

    resp = await client.patch(
        f"/api/v1/regulatory-changes/case-impacts/{impact_id}/acknowledge"
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"


@pytest.mark.asyncio
async def test_mark_impact_not_applicable(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="NA case",
    )
    change = await _make_change(client, affected_case_types=["salary_exchange"])
    scan = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    impact_id = scan.json()["impacts"][0]["id"]

    resp = await client.patch(
        f"/api/v1/regulatory-changes/case-impacts/{impact_id}/not-applicable",
        json={"resolution_note": "Ej tillämpligt för detta ärende."},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "not_applicable"


# ---------------------------------------------------------------------------
# Case impacts listing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_case_impacts(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    case = await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="For impact list",
    )
    change = await _make_change(client, affected_case_types=["salary_exchange"])
    await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")

    resp = await client.get(f"/api/v1/cases/{case.id}/impacts")
    assert resp.status_code == 200
    impacts = resp.json()
    assert len(impacts) == 1
    assert impacts[0]["regulatory_change_id"] == change["id"]
    assert impacts[0]["status"] == "open"


# ---------------------------------------------------------------------------
# Compliance health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_compliance_health(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    client_model = await create_client(
        db_session, test_org.id, test_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="Active 1",
    )
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.PENSION_REVIEW,
        status=CaseStatus.IN_REVIEW,
        title="Active 2",
    )
    # Completed case — excluded from total active
    await create_case(
        db_session, test_org.id, client_model.id, test_user.id,
        case_type=CaseType.PENSION_REVIEW,
        status=CaseStatus.COMPLETED,
        title="Done",
    )

    change_high = await _make_change(
        client, title="High", severity="high",
        affected_case_types=["salary_exchange"],
    )
    change_medium = await _make_change(
        client, title="Medium", severity="medium",
        affected_case_types=["pension_review"],
    )
    await client.post(f"/api/v1/regulatory-changes/{change_high['id']}/scan")
    await client.post(f"/api/v1/regulatory-changes/{change_medium['id']}/scan")

    resp = await client.get("/api/v1/dashboard/compliance-health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_active_cases"] == 2
    assert data["total_open_impacts"] == 2
    assert data["cases_with_open_impacts"] == 2
    assert data["impacts_by_severity"]["high"] == 1
    assert data["impacts_by_severity"]["medium"] == 1
    assert len(data["recent_changes"]) == 2


# ---------------------------------------------------------------------------
# Org isolation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_org_isolation_list(
    client: AsyncClient,
    client_org2: AsyncClient,
):
    await _make_change(client, title="Org1 only")
    resp = await client_org2.get("/api/v1/regulatory-changes")
    assert resp.status_code == 200
    titles = {c["title"] for c in resp.json()}
    assert "Org1 only" not in titles


@pytest.mark.asyncio
async def test_org_isolation_get(
    client: AsyncClient,
    client_org2: AsyncClient,
):
    change = await _make_change(client, title="Hidden")
    resp = await client_org2.get(f"/api/v1/regulatory-changes/{change['id']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_isolation_scan_does_not_touch_other_org(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
    second_org: Organization,
    second_user: User,
):
    # Case in other org that would match
    other_client = await create_client(
        db_session, second_org.id, second_user.id,
        collective_agreement=CollectiveAgreement.ITP1,
    )
    await create_case(
        db_session, second_org.id, other_client.id, second_user.id,
        case_type=CaseType.SALARY_EXCHANGE,
        status=CaseStatus.DRAFT,
        title="Other org case",
    )

    change = await _make_change(
        client, affected_case_types=["salary_exchange"]
    )
    resp = await client.post(f"/api/v1/regulatory-changes/{change['id']}/scan")
    assert resp.status_code == 200
    # No cases in test_org — so 0 impacts, confirming scan didn't cross orgs
    assert resp.json()["new_impacts"] == 0
