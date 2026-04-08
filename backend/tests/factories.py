"""Simple async factory helpers for creating test data.

Each function creates a model instance with sensible defaults and flushes
it to the session. All defaults can be overridden via keyword arguments.
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.models.client_organization import ClientOrganization
from app.models.case import Case
from app.models.knowledge_item import KnowledgeItem
from app.models.audit_entry import AuditEntry
from app.models.recommendation import Recommendation
from app.models.evidence import Evidence
from app.models.base import (
    EmploymentStatus,
    CollectiveAgreement,
    CaseType,
    CaseStatus,
    KnowledgeCategory,
    AuditAction,
    ActorType,
    RecommendationType,
    RecommendationStatus,
    EvidenceSourceType,
)


async def create_client(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, **overrides
) -> Client:
    """Create a test client with sensible defaults."""
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=org_id,
        name="Test Testsson",
        date_of_birth=date(1980, 5, 15),
        employment_status=EmploymentStatus.EMPLOYED,
        collective_agreement=CollectiveAgreement.ITP1,
        annual_income=Decimal("650000.00"),
        desired_retirement_age=65,
        created_by=user_id,
    )
    defaults.update(overrides)
    client = Client(**defaults)
    db.add(client)
    await db.commit()
    return client


async def create_client_organization(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, **overrides
) -> ClientOrganization:
    """Create a test client organization with sensible defaults."""
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=org_id,
        name="Test Företag AB",
        org_number="556123-4567",
        industry="Konsulting",
        collective_agreement=CollectiveAgreement.ITP1,
        contact_person="Test Kontaktperson",
        contact_email="kontakt@testforetag.se",
        employee_count=100,
        created_by=user_id,
    )
    defaults.update(overrides)
    co = ClientOrganization(**defaults)
    db.add(co)
    await db.commit()
    return co


async def create_case(
    db: AsyncSession,
    org_id: uuid.UUID,
    client_id: uuid.UUID,
    user_id: uuid.UUID,
    **overrides,
) -> Case:
    """Create a test case with sensible defaults."""
    defaults = dict(
        id=uuid.uuid4(),
        client_id=client_id,
        assigned_to=user_id,
        organization_id=org_id,
        case_type=CaseType.PENSION_REVIEW,
        status=CaseStatus.DRAFT,
        title="Pensionsöversyn för Test Testsson",
        summary="Genomgång av befintligt pensionssparande",
    )
    defaults.update(overrides)
    case = Case(**defaults)
    db.add(case)
    await db.commit()
    return case


async def create_knowledge_item(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, **overrides
) -> KnowledgeItem:
    """Create a test knowledge item with sensible defaults."""
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="ITP1 Avgiftsstruktur",
        content="ITP1 är ett premiebestämt pensionsavtal med 4.5% på lön under 7.5 IBB.",
        category=KnowledgeCategory.PRODUCT_RULE,
        source="Collectum",
        tags=["ITP1", "avgifter"],
        is_active=True,
        created_by=user_id,
    )
    defaults.update(overrides)
    item = KnowledgeItem(**defaults)
    db.add(item)
    await db.commit()
    return item


async def create_audit_entry(
    db: AsyncSession,
    case_id: uuid.UUID,
    user_id: uuid.UUID,
    **overrides,
) -> AuditEntry:
    """Create a test audit entry."""
    defaults = dict(
        id=uuid.uuid4(),
        case_id=case_id,
        action=AuditAction.CASE_CREATED,
        actor_id=user_id,
        actor_type=ActorType.USER,
        details={},
    )
    defaults.update(overrides)
    entry = AuditEntry(**defaults)
    db.add(entry)
    await db.commit()
    return entry


async def create_recommendation(
    db: AsyncSession,
    case_id: uuid.UUID,
    user_id: uuid.UUID,
    **overrides,
) -> Recommendation:
    """Create a test recommendation."""
    defaults = dict(
        id=uuid.uuid4(),
        case_id=case_id,
        version=1,
        recommendation_type=RecommendationType.PRODUCT_SELECTION,
        summary="Rekommendation att behålla nuvarande val i ITP1.",
        reasoning_chain=[],
        assumptions=[],
        suitability_score=Decimal("0.7500"),
        status=RecommendationStatus.DRAFT,
        created_by=user_id,
    )
    defaults.update(overrides)
    rec = Recommendation(**defaults)
    db.add(rec)
    await db.commit()
    return rec


async def create_evidence(
    db: AsyncSession,
    recommendation_id: uuid.UUID,
    **overrides,
) -> Evidence:
    """Create a test evidence entry."""
    defaults = dict(
        id=uuid.uuid4(),
        recommendation_id=recommendation_id,
        source_type=EvidenceSourceType.PRODUCT_RULE,
        source_reference="Collectum ITP1 handbok",
        content_snippet="ITP1 ger 4.5% premie på lön under taket.",
        relevance_explanation="Direkt relevant för pensionsberäkning.",
        confidence=Decimal("0.95"),
        verified=True,
        verification_status="verified",
    )
    defaults.update(overrides)
    evidence = Evidence(**defaults)
    db.add(evidence)
    await db.commit()
    return evidence
