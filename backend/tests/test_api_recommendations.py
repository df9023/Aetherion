"""Tests for the recommendations API endpoints.

Skips the generate endpoint (requires LLM mock). Tests CRUD and evidence retrieval.
"""

import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.base import RecommendationStatus
from tests.factories import (
    create_client as factory_create_client,
    create_case,
    create_recommendation,
    create_evidence,
)


@pytest.mark.asyncio
async def test_get_recommendation_not_found(client: AsyncClient):
    """GET /api/v1/recommendations/{nonexistent} returns 404."""
    resp = await client.get(f"/api/v1/recommendations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_recommendation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/recommendations/{id} returns the recommendation."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(db_session, case.id, test_user.id)

    resp = await client.get(f"/api/v1/recommendations/{rec.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(rec.id)
    assert data["summary"] == rec.summary
    assert data["version"] == 1


@pytest.mark.asyncio
async def test_get_evidence(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/recommendations/{id}/evidence returns evidence list."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(db_session, case.id, test_user.id)
    ev = await create_evidence(db_session, rec.id)

    resp = await client.get(f"/api/v1/recommendations/{rec.id}/evidence")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["id"] == str(ev.id)
    assert data[0]["source_reference"] == ev.source_reference


@pytest.mark.asyncio
async def test_get_evidence_not_found(client: AsyncClient):
    """GET /api/v1/recommendations/{nonexistent}/evidence returns 404."""
    resp = await client.get(f"/api/v1/recommendations/{uuid.uuid4()}/evidence")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_recommendation_via_api(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """POST /api/v1/recommendations creates a recommendation."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)

    resp = await client.post(
        "/api/v1/recommendations",
        json={
            "case_id": str(case.id),
            "recommendation_type": "product_selection",
            "summary": "Test recommendation via API",
            "reasoning_chain": [
                {
                    "step": 1,
                    "description": "Analysis",
                    "evidence_ids": [],
                    "conclusion": "Test conclusion",
                }
            ],
            "assumptions": [
                {
                    "assumption": "Test assumption",
                    "basis": "Test basis",
                    "impact_if_wrong": "Minimal",
                }
            ],
            "suitability_score": "0.75",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["summary"] == "Test recommendation via API"
    assert data["version"] == 1
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_update_recommendation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /api/v1/recommendations/{id} updates fields."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(db_session, case.id, test_user.id)

    resp = await client.patch(
        f"/api/v1/recommendations/{rec.id}",
        json={"summary": "Updated summary", "status": "pending_review"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "Updated summary"
    assert data["status"] == "pending_review"


@pytest.mark.asyncio
async def test_approve_recommendation_requires_reviewer(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """POST /approve with a non-reviewer user returns 403."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(
        db_session, case.id, test_user.id,
        status=RecommendationStatus.PENDING_REVIEW,
    )

    # test_user is an ADVISOR, not COMPLIANCE_REVIEWER → 403
    resp = await client.post(f"/api/v1/recommendations/{rec.id}/approve")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_approve_recommendation_success(
    reviewer_client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """POST /approve with a reviewer user on a pending_review recommendation succeeds."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(
        db_session, case.id, test_user.id,
        status=RecommendationStatus.PENDING_REVIEW,
    )

    resp = await reviewer_client.post(f"/api/v1/recommendations/{rec.id}/approve")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_cannot_approve_own_recommendation(
    db_session: AsyncSession,
    test_org: Organization,
    reviewer_user: User,
    reviewer_client: AsyncClient,
):
    """A reviewer cannot approve their own recommendation."""
    test_cl = await factory_create_client(db_session, test_org.id, reviewer_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, reviewer_user.id)
    rec = await create_recommendation(
        db_session, case.id, reviewer_user.id,
        status=RecommendationStatus.PENDING_REVIEW,
    )

    resp = await reviewer_client.post(f"/api/v1/recommendations/{rec.id}/approve")
    assert resp.status_code == 403
    assert "own recommendation" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_approve_wrong_status(
    reviewer_client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Cannot approve a recommendation that is not in pending_review status."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(
        db_session, case.id, test_user.id,
        status=RecommendationStatus.DRAFT,
    )

    resp = await reviewer_client.post(f"/api/v1/recommendations/{rec.id}/approve")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_case_recommendations(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """GET /api/v1/cases/{id}/recommendations returns recommendation list."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    rec = await create_recommendation(db_session, case.id, test_user.id)

    resp = await client.get(f"/api/v1/cases/{case.id}/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["id"] == str(rec.id)
