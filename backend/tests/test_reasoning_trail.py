"""Tests for the reasoning trail annotation and review endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.base import RecommendationStatus
from tests.factories import (
    create_client as factory_create_client,
    create_case,
    create_recommendation,
)


def _make_reasoning_chain() -> list[dict]:
    return [
        {
            "step": 1,
            "title": "Behovsanalys",
            "description": "Klienten har ett ITP1-avtal.",
            "evidence_ids": [],
            "cited_texts": [
                {
                    "text": "ITP1 ger 4.5% premie",
                    "source_title": "Collectum handbok",
                    "knowledge_item_id": None,
                }
            ],
            "conclusion": "Behov identifierat.",
        },
        {
            "step": 2,
            "title": "Kunskapsbedömning",
            "description": "Klienten har grundläggande pensionskunskap.",
            "evidence_ids": [],
            "cited_texts": [],
            "conclusion": "Kunskap bedömd.",
        },
        {
            "step": 3,
            "title": "Kostnadsinformation",
            "description": "Kostnadsinformation (IDD-krav)",
            "evidence_ids": [],
            "cited_texts": [],
            "conclusion": "Avgifter 0.3% per år.",
        },
    ]


# ---------------------------------------------------------------------------
# Backward compatibility: old chains without new fields still work
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_old_reasoning_chain_backward_compatible(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Recommendations with old-format reasoning_chain (no title/cited_texts) still serialize."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    # Old-style chain without title or cited_texts
    old_chain = [
        {"step": 1, "description": "Analysis", "evidence_ids": [], "conclusion": "Done."}
    ]
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=old_chain
    )

    resp = await client.get(f"/api/v1/recommendations/{rec.id}")
    assert resp.status_code == 200
    data = resp.json()
    step = data["reasoning_chain"][0]
    assert step["step"] == 1
    assert step["description"] == "Analysis"
    # New fields default to None/empty
    assert step.get("title") is None
    assert step.get("cited_texts") == [] or step.get("cited_texts") is None


# ---------------------------------------------------------------------------
# New reasoning chain with titles and cited_texts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_new_reasoning_chain_with_titles(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Recommendations with new-format reasoning_chain include title and cited_texts."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    resp = await client.get(f"/api/v1/recommendations/{rec.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reasoning_chain"][0]["title"] == "Behovsanalys"
    assert len(data["reasoning_chain"][0]["cited_texts"]) == 1
    assert data["reasoning_chain"][0]["cited_texts"][0]["text"] == "ITP1 ger 4.5% premie"


# ---------------------------------------------------------------------------
# Annotate reasoning step
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_annotate_reasoning_step(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """PATCH /recommendations/{id}/reasoning/{step}/annotate adds annotation."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    resp = await client.patch(
        f"/api/v1/recommendations/{rec.id}/reasoning/1/annotate",
        json={"advisor_annotation": "Verifierat mot Collectum handbok."},
    )
    assert resp.status_code == 200
    data = resp.json()
    step1 = data["reasoning_chain"][0]
    assert step1["advisor_annotation"] == "Verifierat mot Collectum handbok."
    assert step1["annotated_by"] == str(test_user.id)
    assert step1["annotated_at"] is not None


@pytest.mark.asyncio
async def test_annotate_nonexistent_step(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Annotating a step that doesn't exist returns 404."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    resp = await client.patch(
        f"/api/v1/recommendations/{rec.id}/reasoning/99/annotate",
        json={"advisor_annotation": "Nope"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_annotate_creates_audit_entry(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Annotating a step creates a reasoning_annotated audit entry."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    await client.patch(
        f"/api/v1/recommendations/{rec.id}/reasoning/1/annotate",
        json={"advisor_annotation": "Stämmer."},
    )

    resp = await client.get(f"/api/v1/cases/{case.id}/audit")
    assert resp.status_code == 200
    actions = [e["action"] for e in resp.json()]
    assert "reasoning_annotated" in actions


# ---------------------------------------------------------------------------
# Review reasoning
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_review_reasoning(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """POST /recommendations/{id}/reasoning/review sets review_status to reviewed."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session,
        case.id,
        test_user.id,
        reasoning_chain=chain,
        reasoning_metadata={"review_status": "pending"},
    )

    resp = await client.post(
        f"/api/v1/recommendations/{rec.id}/reasoning/review",
        json={"comment": "Alla steg verifierade."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reasoning_metadata"]["review_status"] == "reviewed"
    assert data["reasoning_metadata"]["reviewed_by"] == str(test_user.id)
    assert data["reasoning_metadata"]["reviewed_at"] is not None
    assert data["reasoning_metadata"]["review_comment"] == "Alla steg verifierade."


@pytest.mark.asyncio
async def test_review_reasoning_without_comment(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Review works without a comment."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    resp = await client.post(
        f"/api/v1/recommendations/{rec.id}/reasoning/review",
        json={},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reasoning_metadata"]["review_status"] == "reviewed"
    assert data["reasoning_metadata"].get("review_comment") is None


@pytest.mark.asyncio
async def test_review_creates_audit_entry(
    client: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Reviewing reasoning creates a reasoning_reviewed audit entry."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    await client.post(
        f"/api/v1/recommendations/{rec.id}/reasoning/review",
        json={},
    )

    resp = await client.get(f"/api/v1/cases/{case.id}/audit")
    assert resp.status_code == 200
    actions = [e["action"] for e in resp.json()]
    assert "reasoning_reviewed" in actions


# ---------------------------------------------------------------------------
# Org isolation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_annotate_org_isolation(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Cannot annotate a recommendation from another organization."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    resp = await client_org2.patch(
        f"/api/v1/recommendations/{rec.id}/reasoning/1/annotate",
        json={"advisor_annotation": "Trying cross-org annotation"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_review_org_isolation(
    client: AsyncClient,
    client_org2: AsyncClient,
    db_session: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    """Cannot review reasoning from another organization."""
    test_cl = await factory_create_client(db_session, test_org.id, test_user.id)
    case = await create_case(db_session, test_org.id, test_cl.id, test_user.id)
    chain = _make_reasoning_chain()
    rec = await create_recommendation(
        db_session, case.id, test_user.id, reasoning_chain=chain
    )

    resp = await client_org2.post(
        f"/api/v1/recommendations/{rec.id}/reasoning/review",
        json={},
    )
    assert resp.status_code == 404
