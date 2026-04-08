"""
Seed script for Aetherion development database.

Populates:
- 1 organization (fictional Swedish advisory firm)
- 2 users (admin + advisor)
- 2 clients with realistic Swedish pension situations
- 1 case per client
- Knowledge items with embeddings for RAG retrieval
- Knowledge documents from backend/data/knowledge/ (PDF/TXT + .meta.json)

Usage:
    cd backend
    source .venv/bin/activate
    python -m scripts.seed
"""

import asyncio
import hashlib
import json
import logging
import sys
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable, Awaitable

# Ensure the backend package is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session_maker, engine

logger = logging.getLogger(__name__)
from app.models.organization import Organization
from app.models.user import User
from app.models.client import Client
from app.models.client_organization import ClientOrganization
from app.models.case import Case
from app.models.audit_entry import AuditEntry
from app.models.knowledge_item import KnowledgeItem
from app.models.regulatory_change import RegulatoryChange
from app.models.case_impact import CaseImpact
from app.models.base import (
    OrganizationType,
    UserRole,
    EmploymentStatus,
    CollectiveAgreement,
    RiskProfile,
    CaseImpactStatus,
    CaseType,
    CaseStatus,
    KnowledgeCategory,
    AuditAction,
    ActorType,
    RegulatoryChangeSeverity,
)


# ---------------------------------------------------------------------------
# Deterministic UUIDs (reproducible seeds)
# ---------------------------------------------------------------------------
def _uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_DNS, f"aetherion.seed.{name}")


ORG_ID = _uuid("org.spp")
USER_ADMIN_ID = _uuid("user.admin.eriksson.spp")
USER_ADVISOR_ID = _uuid("user.advisor.lindqvist.spp")
CLIENT_1_ID = _uuid("client.anna.johansson")
CLIENT_2_ID = _uuid("client.lars.pettersson")
CLIENT_ORG_1_ID = _uuid("client_org.mckinsey_stockholm")
CLIENT_ORG_2_ID = _uuid("client_org.volvo_goteborg")
CLIENT_ORG_3_ID = _uuid("client_org.scandic_hotels")
CASE_1_ID = _uuid("case.anna.retirement")
CASE_2_ID = _uuid("case.lars.lonvaxling")

KI_IDS = [_uuid(f"knowledge.{i}") for i in range(6)]

REG_CHANGE_FFFS_ID = _uuid("reg_change.fffs_2026_4")
REG_CHANGE_IBB_ID = _uuid("reg_change.ibb_2026")
REG_CHANGE_COLLECTUM_ID = _uuid("reg_change.collectum_itp1_2026_07")


# ---------------------------------------------------------------------------
# Fake embedding generator — deterministic, dimension-correct (1536)
# ---------------------------------------------------------------------------
def fake_embedding(text_content: str) -> list[float]:
    """Generate a deterministic 1536-dim pseudo-embedding from text content.

    Uses overlapping hash windows so semantically related content
    (sharing words/phrases) produces closer vectors than unrelated content.
    Good enough for testing cosine similarity retrieval.
    """
    words = text_content.lower().split()
    vec = [0.0] * 1536

    # Hash individual words and bigrams into the vector
    for i, word in enumerate(words):
        h = hashlib.sha256(word.encode()).digest()
        for j in range(0, min(32, len(h)), 2):
            idx = int.from_bytes(h[j : j + 2], "big") % 1536
            vec[idx] += 1.0

        # Bigrams
        if i + 1 < len(words):
            bigram = f"{word} {words[i + 1]}"
            h2 = hashlib.sha256(bigram.encode()).digest()
            for j in range(0, min(32, len(h2)), 2):
                idx = int.from_bytes(h2[j : j + 2], "big") % 1536
                vec[idx] += 0.5

    # Normalize to unit vector
    magnitude = sum(v * v for v in vec) ** 0.5
    if magnitude > 0:
        vec = [v / magnitude for v in vec]

    return vec


# ---------------------------------------------------------------------------
# Knowledge item content
# ---------------------------------------------------------------------------
KNOWLEDGE_ITEMS = [
    {
        "id": KI_IDS[0],
        "title": "ITP1 — Premiebestämd tjänstepension",
        "category": KnowledgeCategory.PRODUCT_RULE,
        "source": "Collectum — ITP1-avtalet 2024",
        "tags": ["ITP1", "premiebestämd", "collectum", "tjänstepension"],
        "content": (
            "ITP1 är en premiebestämd tjänstepension som gäller för privatanställda "
            "tjänstemän födda 1979 eller senare. Premien är 4,5% på lönedelar upp till "
            "7,5 inkomstbasbelopp (ibb) och 30% på lönedelar däröver. Arbetstagaren "
            "väljer själv förvaltningsform (traditionell eller fondförvaltning) och "
            "leverantör via Collectums valcentral. Om inget aktivt val görs placeras "
            "premierna i Collectums defaultalternativ. Avgiftsuttag varierar mellan "
            "0,10% och 0,90% beroende på fondval. ITP1 inkluderar inte automatiskt "
            "återbetalningsskydd — detta måste väljas aktivt och minskar den egna "
            "pensionen med cirka 2-4%. Utbetalning sker normalt från 65 års ålder, "
            "men kan tas ut från 55 år med reducerat belopp."
        ),
    },
    {
        "id": KI_IDS[1],
        "title": "ITP2 — Förmånsbestämd tjänstepension",
        "category": KnowledgeCategory.PRODUCT_RULE,
        "source": "Collectum — ITP2-avtalet 2024",
        "tags": ["ITP2", "förmånsbestämd", "alecta", "tjänstepension"],
        "content": (
            "ITP2 är en förmånsbestämd tjänstepension som gäller för privatanställda "
            "tjänstemän födda 1978 eller tidigare. Pensionen baseras på slutlönen och "
            "beräknas som: 10% på lönedelar mellan 0-7,5 ibb, 65% mellan 7,5-20 ibb, "
            "och 32,5% mellan 20-30 ibb. Alecta är huvudleverantör och förvaltar den "
            "förmånsbestämda delen. Det finns en premiebestämd del (ITPK) om 2% på "
            "hela lönen där den anställde väljer förvaltare. ITP2 ger normalt högre "
            "pension än ITP1 för anställda med hög slutlön. Löneväxling inom ITP2 "
            "kräver särskild analys då den kan påverka den förmånsbestämda nivån "
            "negativt om lönen sjunker under 7,5 ibb. Familjepension och "
            "sjukpension ingår automatiskt."
        ),
    },
    {
        "id": KI_IDS[2],
        "title": "Löneväxling — regler och förutsättningar",
        "category": KnowledgeCategory.INTERNAL_POLICY,
        "source": "SPP — Intern policy 2024-01",
        "tags": ["löneväxling", "salary_exchange", "tjänstepension", "skatt"],
        "content": (
            "Löneväxling innebär att den anställde avstår en del av bruttolönen mot "
            "att arbetsgivaren gör en extra pensionsinbetalning. Skatteeffekten gör "
            "att löneväxling normalt är förmånligt vid månadslöner över ca 44 000 kr "
            "(2024), dvs över brytpunkten för statlig inkomstskatt. Viktiga "
            "överväganden: (1) Löneväxling sänker sjukpenninggrundande inkomst (SGI), "
            "föräldrapenning och a-kassa. (2) Vid ITP2 kan löneväxling under 7,5 ibb "
            "sänka den förmånsbestämda pensionen. (3) Arbetsgivaren sparar sociala "
            "avgifter men betalar särskild löneskatt (24,26%). (4) Maximum att "
            "löneväxla bör begränsas så att kontant lön inte understiger nivå som "
            "påverkar socialförsäkringsförmåner negativt. Rekommendation: löneväxla "
            "max 30% av lönedelar över 7,5 ibb."
        ),
    },
    {
        "id": KI_IDS[3],
        "title": "IDD — Krav på behovsanalys och lämplighetsbedömning",
        "category": KnowledgeCategory.REGULATORY_REQUIREMENT,
        "source": "Finansinspektionen — FFFS 2018:10, IDD-implementering",
        "tags": ["IDD", "behovsanalys", "lämplighetsbedömning", "compliance", "FI"],
        "content": (
            "Enligt IDD (Insurance Distribution Directive) och Finansinspektionens "
            "föreskrifter FFFS 2018:10 ska en rådgivare genomföra: (1) Behovsanalys "
            "(demands and needs test) — kartlägga kundens behov, önskemål och "
            "ekonomiska situation innan en rekommendation lämnas. (2) "
            "Lämplighetsbedömning (suitability assessment) — bedöma att den "
            "rekommenderade produkten/lösningen är lämplig med hänsyn till kundens "
            "kunskapsnivå och erfarenhet, ekonomiska situation, samt investeringsmål "
            "inklusive risktolerans. (3) Kostnadstransparens — ge kunden tydlig "
            "information om alla avgifter och kostnader, inklusive påverkan på "
            "avkastning. (4) Intressekonflikter — identifiera och hantera "
            "intressekonflikter, och informera kunden. Dokumentation ska sparas "
            "minst 10 år. Brister i dokumentation eller behovsanalys är den "
            "vanligaste anledningen till FI-sanktioner mot rådgivare."
        ),
    },
    {
        "id": KI_IDS[4],
        "title": "Riskprofiler — bedömning och rekommendation",
        "category": KnowledgeCategory.PLAYBOOK,
        "source": "SPP — Riskprofilsguide v3",
        "tags": ["riskprofil", "fondalloallokering", "rådgivning", "lämplighetsbedömning"],
        "content": (
            "Riskprofilen avgör rekommenderad tillgångsfördelning. Bedömning ska "
            "inkludera: (1) Placeringshorisont — antal år till pensionsuttag. "
            ">15 år: kan bära hög risk. 5-15 år: moderat risk. <5 år: låg risk. "
            "(2) Risktolerans — kundens inställning till värdesvängningar. "
            "(3) Riskkapacitet — kundens ekonomiska förmåga att hantera förluster. "
            "Rekommenderad fördelning: Låg risk: 70% räntor/30% aktier. "
            "Moderat risk: 40% räntor/60% aktier. Hög risk: 10% räntor/90% aktier. "
            "Nedtrappning bör ske automatiskt de sista 10 åren före pensionering. "
            "En kund med hög inkomst och lång horisont men låg risktolerans ska "
            "placeras enligt den lägsta av risk-kapacitet och risk-tolerans."
        ),
    },
    {
        "id": KI_IDS[5],
        "title": "Pensionsålder och uttag — regler 2024",
        "category": KnowledgeCategory.REGULATORY_REQUIREMENT,
        "source": "Pensionsmyndigheten / SKV — regelverk 2024",
        "tags": ["pensionsålder", "uttag", "allmän_pension", "skatt"],
        "content": (
            "Lägsta ålder för uttag av allmän pension höjdes till 63 år 2023 och "
            "planeras höjas till 64 år 2026. Tjänstepension kan normalt tas ut från "
            "55 år (ITP) men utbetalningen blir lägre vid tidigt uttag. Riktålder "
            "för pension (den ålder då pensionssystemet är dimensionerat för) är "
            "67 år från 2026. LAS-åldern (rätt att kvarstå i anställning) höjdes "
            "till 69 år. Skattemässigt: pensionsinkomst beskattas som "
            "inkomst av tjänst. Jobbskatteavdraget gäller inte för pensionsinkomst, "
            "vilket innebär att skatten på pensionsinkomst är högre jämfört med "
            "löneinkomst vid samma bruttoinkomst. Samordning av uttag (ta "
            "tjänstepension tidigt, skjut upp allmän pension) kan vara skattemässigt "
            "fördelaktigt. Varje år som allmän pension skjuts upp ökar utbetalningen "
            "med ca 6-8% per år i nuvarande system."
        ),
    },
]


# ---------------------------------------------------------------------------
# Embedding helper — real or fake depending on env
# ---------------------------------------------------------------------------
async def _get_embed_fn():
    """Return an async embedding function.

    Uses OpenAI text-embedding-3-small when OPENAI_API_KEY is set,
    otherwise falls back to the deterministic fake_embedding().
    """
    settings = get_settings()
    if settings.openai_api_key:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        print("  Using OpenAI text-embedding-3-small for real embeddings")

        async def _real(text: str) -> list[float]:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding

        return _real

    print("  OPENAI_API_KEY not set — using hash-based fake embeddings")

    async def _fake(text: str) -> list[float]:
        return fake_embedding(text)

    return _fake


# ---------------------------------------------------------------------------
# Knowledge document ingestion from backend/data/knowledge/
# ---------------------------------------------------------------------------
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge"


def _doc_chunk_uuid(filename: str, chunk_index: int) -> uuid.UUID:
    """Deterministic UUID for a document chunk — idempotent across re-seeds."""
    return uuid.uuid5(uuid.NAMESPACE_DNS, f"aetherion.seed.doc.{filename}.chunk.{chunk_index}")


async def seed_knowledge_documents(
    db: AsyncSession,
    embed_fn: Callable[[str], Awaitable[list[float]]],
    org_id: uuid.UUID,
    user_id: uuid.UUID,
) -> int:
    """Ingest PDFs/TXTs from backend/data/knowledge/ into knowledge items."""
    if not KNOWLEDGE_DIR.exists():
        print(f"  Knowledge dir not found: {KNOWLEDGE_DIR}")
        return 0

    meta_files = sorted(KNOWLEDGE_DIR.glob("*.meta.json"))
    if not meta_files:
        print("  No .meta.json files found in data/knowledge/")
        return 0

    from app.services.chunker import ChunkerService

    chunker = ChunkerService()
    total_created = 0

    for meta_path in meta_files:
        base_name = meta_path.name.removesuffix(".meta.json")

        # Load metadata
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  WARN: Skipping {meta_path.name} — invalid JSON: {e}")
            continue

        title = meta.get("title", base_name)
        category_str = meta.get("category", "product_rule")
        source = meta.get("source", base_name)
        tags = meta.get("tags", [])

        try:
            category = KnowledgeCategory(category_str)
        except ValueError:
            print(f"  WARN: Skipping {base_name} — invalid category '{category_str}'")
            continue

        # Find matching document file (PDF or TXT)
        pdf_path = KNOWLEDGE_DIR / f"{base_name}.pdf"
        txt_path = KNOWLEDGE_DIR / f"{base_name}.txt"

        if pdf_path.exists():
            import io
            import pdfplumber

            try:
                text_parts: list[str] = []
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        if page_text.strip():
                            text_parts.append(page_text)
                full_text = "\n\n".join(text_parts)
            except Exception as e:
                print(f"  WARN: Failed to extract text from {pdf_path.name}: {e}")
                continue
        elif txt_path.exists():
            try:
                full_text = txt_path.read_text(encoding="utf-8")
            except OSError as e:
                print(f"  WARN: Failed to read {txt_path.name}: {e}")
                continue
        else:
            print(f"  WARN: No .pdf or .txt file found for {base_name}, skipping")
            continue

        if not full_text.strip():
            print(f"  WARN: {base_name} produced no text, skipping")
            continue

        # Chunk the document
        chunks = chunker.chunk_document(
            text=full_text,
            source_title=source,
            metadata={"filename": base_name},
        )

        if not chunks:
            print(f"  WARN: {base_name} produced no chunks, skipping")
            continue

        # Compute deterministic IDs for all chunks of this file
        chunk_ids = [_doc_chunk_uuid(base_name, i) for i in range(len(chunks))]

        # Delete any existing items with these IDs (idempotent re-seed)
        for cid in chunk_ids:
            await db.execute(
                text("DELETE FROM knowledge_items WHERE id = :id"),
                {"id": cid},
            )

        # Create knowledge items
        for i, chunk in enumerate(chunks):
            chunk_id = chunk_ids[i]

            if chunk.section_heading:
                chunk_title = f"{title} — {chunk.section_heading}"
            else:
                chunk_title = f"{title} — Del {i + 1}"

            chunk_tags = list(tags)
            if chunk.section_heading:
                heading_tag = chunk.section_heading.strip().lower()[:50]
                if heading_tag not in chunk_tags:
                    chunk_tags.append(heading_tag)

            embedding = await embed_fn(chunk.content)

            ki = KnowledgeItem(
                id=chunk_id,
                organization_id=org_id,
                title=chunk_title,
                content=chunk.content,
                category=category,
                source=source,
                tags=chunk_tags,
                embedding=embedding,
                is_active=True,
                created_by=user_id,
                source_location=chunk.source_location if chunk.source_location else None,
            )
            db.add(ki)

        await db.flush()
        total_created += len(chunks)
        print(f"  {base_name}: {len(chunks)} chunks ingested")

    return total_created


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------
async def seed() -> None:
    async with async_session_maker() as db:
        # Check if already seeded
        existing = await db.execute(
            text("SELECT id FROM organizations WHERE id = :id"),
            {"id": ORG_ID},
        )
        if existing.scalar_one_or_none():
            print("Database already seeded. Truncating and re-seeding...")

        print("Cleaning all seed data...")
        await db.execute(text("DELETE FROM case_impacts"))
        await db.execute(text("DELETE FROM regulatory_changes"))
        await db.execute(text("DELETE FROM firm_insights"))
        await db.execute(text("DELETE FROM audit_entries"))
        await db.execute(text("DELETE FROM evidences"))
        await db.execute(text("DELETE FROM workflows"))
        await db.execute(text("DELETE FROM documents"))
        await db.execute(text("DELETE FROM recommendations"))
        await db.execute(text("DELETE FROM cases"))
        await db.execute(text("DELETE FROM clients"))
        await db.execute(text("DELETE FROM client_organizations"))
        await db.execute(text("DELETE FROM knowledge_items"))
        await db.execute(text("DELETE FROM users"))
        await db.execute(text("DELETE FROM organizations"))
        await db.commit()

        print("Seeding organization...")
        org = Organization(
            id=ORG_ID,
            name="SPP",
            org_type=OrganizationType.PENSION_PROVIDER,
            jurisdiction="SE",
            settings={
                "default_language": "sv",
                "risk_assessment_model": "three_tier",
                "compliance_auto_check": True,
            },
        )
        db.add(org)
        await db.flush()

        print("Seeding users...")
        admin = User(
            id=USER_ADMIN_ID,
            organization_id=ORG_ID,
            email="erik.eriksson@spp.se",
            name="Erik Eriksson",
            role=UserRole.ADMIN,
            workos_user_id="workos_dev_admin_001",
        )
        advisor = User(
            id=USER_ADVISOR_ID,
            organization_id=ORG_ID,
            email="maria.lindqvist@spp.se",
            name="Maria Lindqvist",
            role=UserRole.ADVISOR,
            workos_user_id="workos_dev_advisor_001",
        )
        db.add_all([admin, advisor])
        await db.flush()

        print("Seeding clients...")
        client_1 = Client(
            id=CLIENT_1_ID,
            organization_id=ORG_ID,
            name="Anna Johansson",
            date_of_birth=date(1981, 3, 15),
            employment_status=EmploymentStatus.EMPLOYED,
            employer_name="Volvo Group AB",
            collective_agreement=CollectiveAgreement.ITP1,
            annual_income=Decimal("684000.00"),  # 57 000 kr/mån
            desired_retirement_age=65,
            risk_profile=RiskProfile.MODERATE,
            created_by=USER_ADVISOR_ID,
        )
        client_2 = Client(
            id=CLIENT_2_ID,
            organization_id=ORG_ID,
            name="Lars Pettersson",
            date_of_birth=date(1968, 8, 22),
            employment_status=EmploymentStatus.EMPLOYED,
            employer_name="Ericsson AB",
            collective_agreement=CollectiveAgreement.ITP2,
            annual_income=Decimal("960000.00"),  # 80 000 kr/mån
            desired_retirement_age=63,
            risk_profile=RiskProfile.LOW,
            created_by=USER_ADVISOR_ID,
        )
        db.add_all([client_1, client_2])
        await db.flush()

        print("Seeding client organizations...")
        co_1 = ClientOrganization(
            id=CLIENT_ORG_1_ID,
            organization_id=ORG_ID,
            name="McKinsey & Company Stockholm",
            org_number="556109-9101",
            industry="Managementkonsulting",
            collective_agreement=CollectiveAgreement.ITP1,
            contact_person="Lisa Bergström",
            contact_email="lisa.bergstrom@mckinsey.com",
            employee_count=450,
            created_by=USER_ADVISOR_ID,
        )
        co_2 = ClientOrganization(
            id=CLIENT_ORG_2_ID,
            organization_id=ORG_ID,
            name="Volvo Cars Göteborg",
            org_number="556074-3089",
            industry="Fordonsindustri",
            collective_agreement=CollectiveAgreement.SAF_LO,
            contact_person="Anders Nilsson",
            contact_email="anders.nilsson@volvocars.com",
            employee_count=12000,
            created_by=USER_ADVISOR_ID,
        )
        co_3 = ClientOrganization(
            id=CLIENT_ORG_3_ID,
            organization_id=ORG_ID,
            name="Scandic Hotels AB",
            org_number="556299-1009",
            industry="Hotell & Restaurang",
            collective_agreement=CollectiveAgreement.OTHER,
            contact_person="Maria Svensson",
            contact_email="maria.svensson@scandichotels.com",
            employee_count=3200,
            created_by=USER_ADVISOR_ID,
        )
        db.add_all([co_1, co_2, co_3])
        await db.flush()

        # Link existing clients to their client organizations
        client_1.client_organization_id = CLIENT_ORG_1_ID
        client_2.client_organization_id = CLIENT_ORG_2_ID
        await db.flush()

        print("Seeding cases...")
        case_1 = Case(
            id=CASE_1_ID,
            client_id=CLIENT_1_ID,
            assigned_to=USER_ADVISOR_ID,
            organization_id=ORG_ID,
            case_type=CaseType.RETIREMENT_PLANNING,
            status=CaseStatus.IN_PREPARATION,
            title="Pensionsöversikt och placeringsrådgivning — Anna Johansson",
            summary=(
                "Anna, 45 år, ITP1 via Volvo. Vill se över sin tjänstepension "
                "och eventuellt göra ett aktivt fondval. Har aldrig gjort ett aktivt "
                "val hos Collectum."
            ),
        )
        case_2 = Case(
            id=CASE_2_ID,
            client_id=CLIENT_2_ID,
            assigned_to=USER_ADVISOR_ID,
            organization_id=ORG_ID,
            case_type=CaseType.SALARY_EXCHANGE,
            status=CaseStatus.IN_PREPARATION,
            title="Löneväxlingsanalys — Lars Pettersson",
            summary=(
                "Lars, 58 år, ITP2 via Ericsson. Hög lön (80 000 kr/mån). "
                "Vill utreda löneväxling men har ITP2 förmånsbestämd pension — "
                "kräver noggrann analys av påverkan på den förmånsbestämda delen."
            ),
        )
        db.add_all([case_1, case_2])
        await db.flush()

        # Audit entries for case creation
        for case, client_name in [(case_1, "Anna Johansson"), (case_2, "Lars Pettersson")]:
            audit = AuditEntry(
                case_id=case.id,
                action=AuditAction.CASE_CREATED,
                actor_id=USER_ADVISOR_ID,
                actor_type=ActorType.USER,
                details={
                    "case_type": case.case_type.value,
                    "client_name": client_name,
                },
            )
            db.add(audit)

        print("Seeding knowledge items with embeddings...")
        embed = await _get_embed_fn()
        for ki_data in KNOWLEDGE_ITEMS:
            embedding = await embed(ki_data["content"])
            ki = KnowledgeItem(
                id=ki_data["id"],
                organization_id=ORG_ID,
                title=ki_data["title"],
                content=ki_data["content"],
                category=ki_data["category"],
                source=ki_data["source"],
                tags=ki_data["tags"],
                embedding=embedding,
                is_active=True,
                created_by=USER_ADMIN_ID,
            )
            db.add(ki)

        await db.flush()

        print("Seeding knowledge from documents...")
        doc_count = await seed_knowledge_documents(db, embed, ORG_ID, USER_ADMIN_ID)

        print("Seeding regulatory changes...")
        now = datetime.now(timezone.utc)
        reg_changes = [
            RegulatoryChange(
                id=REG_CHANGE_FFFS_ID,
                organization_id=ORG_ID,
                created_by=USER_ADMIN_ID,
                title="FFFS 2026:4 — Uppdaterade dokumentationskrav för löneväxling",
                description=(
                    "Finansinspektionen publicerade den 3 april 2026 FFFS 2026:4 med "
                    "skärpta dokumentationskrav för rådgivning om löneväxling ovanför "
                    "inkomsttaket. Rådgivare måste nu explicit dokumentera hur SGI-påverkan "
                    "har diskuterats med klienten samt bifoga en skriftlig bekräftelse "
                    "från arbetsgivaren innan rekommendationen kan slutföras. Ikraftträdande "
                    "2026-05-01."
                ),
                source="Finansinspektionen",
                source_url="https://fi.se/sv/publicerat/foreskrifter/2026/fffs-2026-4/",
                severity=RegulatoryChangeSeverity.HIGH,
                affected_case_types=[CaseType.SALARY_EXCHANGE.value],
                affected_agreements=[
                    CollectiveAgreement.ITP1.value,
                    CollectiveAgreement.ITP2.value,
                ],
                affected_tags=["löneväxling", "dokumentation", "SGI"],
                is_active=True,
                published_at=now,
            ),
            RegulatoryChange(
                id=REG_CHANGE_IBB_ID,
                organization_id=ORG_ID,
                created_by=USER_ADMIN_ID,
                title="IBB 2026 fastställt till 85 600 SEK",
                description=(
                    "Inkomstbasbeloppet (IBB) för 2026 har fastställts av regeringen till "
                    "85 600 SEK. Detta påverkar beräkningen av inkomsttaket (7,5 IBB = "
                    "642 000 SEK/år eller 53 500 SEK/mån) som används i alla "
                    "pensionsberäkningar. Alla aktiva ärenden bör granskas för att "
                    "säkerställa att rätt IBB används i beräkningar och rekommendationer."
                ),
                source="Regeringen / SCB",
                source_url="https://www.scb.se/hitta-statistik/statistik-efter-amne/priser-och-konsumtion/konsumentprisindex/konsumentprisindex-kpi/pong/tabell-och-diagram/inkomstbasbelopp/",
                severity=RegulatoryChangeSeverity.MEDIUM,
                affected_case_types=[
                    CaseType.PENSION_REVIEW.value,
                    CaseType.TRANSFER_ADVICE.value,
                    CaseType.SALARY_EXCHANGE.value,
                    CaseType.RETIREMENT_PLANNING.value,
                    CaseType.DECUMULATION.value,
                ],
                affected_agreements=[],
                affected_tags=["IBB", "inkomsttak", "beräkning"],
                is_active=True,
                published_at=now,
            ),
            RegulatoryChange(
                id=REG_CHANGE_COLLECTUM_ID,
                organization_id=ORG_ID,
                created_by=USER_ADMIN_ID,
                title="Collectum: Nya regler för ITP1-val från 2026-07-01",
                description=(
                    "Collectum har aviserat att ITP1-tjänstepensionsvalet ändras från "
                    "1 juli 2026. Nya regler för återbetalningsskydd, fondutbud och "
                    "avgifter införs. Rådgivare bör informera klienter med ITP1 som "
                    "överväger att göra ett aktivt val om de nya reglerna och "
                    "eventuellt avvakta till efter ikraftträdandet."
                ),
                source="Collectum",
                source_url="https://www.collectum.se/nyheter/itp1-andringar-2026",
                severity=RegulatoryChangeSeverity.MEDIUM,
                affected_case_types=[
                    CaseType.PENSION_REVIEW.value,
                    CaseType.RETIREMENT_PLANNING.value,
                ],
                affected_agreements=[CollectiveAgreement.ITP1.value],
                affected_tags=["ITP1", "Collectum", "fondval"],
                is_active=True,
                published_at=now,
            ),
        ]
        for rc in reg_changes:
            db.add(rc)
            db.add(
                AuditEntry(
                    case_id=None,
                    action=AuditAction.REGULATORY_CHANGE_CREATED,
                    actor_id=USER_ADMIN_ID,
                    actor_type=ActorType.USER,
                    details={
                        "regulatory_change_id": str(rc.id),
                        "title": rc.title,
                        "severity": rc.severity.value,
                    },
                )
            )
        await db.flush()

        print("Auto-scanning regulatory changes against active cases...")
        active_cases = [case_1, case_2]
        client_map = {CLIENT_1_ID: client_1, CLIENT_2_ID: client_2}
        total_impacts = 0
        for rc in reg_changes:
            affected_case_types = set(rc.affected_case_types or [])
            affected_agreements = set(rc.affected_agreements or [])
            for case in active_cases:
                if case.status in (CaseStatus.ARCHIVED, CaseStatus.COMPLETED):
                    continue
                case_client = client_map[case.client_id]
                case_type_value = case.case_type.value
                agreement_value = (
                    case_client.collective_agreement.value
                    if case_client.collective_agreement
                    else None
                )
                matched_case_type = (
                    bool(affected_case_types)
                    and case_type_value in affected_case_types
                )
                matched_agreement = (
                    bool(affected_agreements)
                    and agreement_value is not None
                    and agreement_value in affected_agreements
                )
                if not (matched_case_type or matched_agreement):
                    continue
                reasons = []
                sections = []
                if matched_case_type:
                    reasons.append(
                        f"Ärendetyp ({case_type_value}) ingår i den reglering som ändrats"
                    )
                    sections.append("case_type")
                if matched_agreement:
                    reasons.append(
                        f"Kollektivavtal ({agreement_value}) påverkas av ändringen"
                    )
                    sections.append("collective_agreement")
                match_reason = f"{rc.title}. " + " · ".join(reasons) + "."
                impact = CaseImpact(
                    organization_id=ORG_ID,
                    regulatory_change_id=rc.id,
                    case_id=case.id,
                    match_reason=match_reason,
                    affected_sections=sections,
                    status=CaseImpactStatus.OPEN,
                )
                db.add(impact)
                total_impacts += 1
        await db.flush()
        print(f"  Created {total_impacts} case impact(s)")

        await db.commit()

        print()
        print("=" * 60)
        print("Seed complete!")
        print("=" * 60)
        print(f"Organization:  {ORG_ID}  SPP")
        print(f"Admin user:    {USER_ADMIN_ID}  erik.eriksson@spp.se")
        print(f"Advisor user:  {USER_ADVISOR_ID}  maria.lindqvist@spp.se")
        print(f"Client 1:      {CLIENT_1_ID}  Anna Johansson (ITP1, 45 yr)")
        print(f"Client 2:      {CLIENT_2_ID}  Lars Pettersson (ITP2, 58 yr)")
        print(f"Client Org 1:  {CLIENT_ORG_1_ID}  McKinsey Stockholm")
        print(f"Client Org 2:  {CLIENT_ORG_2_ID}  Volvo Göteborg")
        print(f"Client Org 3:  {CLIENT_ORG_3_ID}  Scandic Hotels")
        print(f"Case 1:        {CASE_1_ID}  Retirement planning")
        print(f"Case 2:        {CASE_2_ID}  Löneväxling")
        print(f"Knowledge:     {len(KNOWLEDGE_ITEMS)} base items + {doc_count} document chunks")
        print(f"Reg changes:   {len(reg_changes)} seeded, {total_impacts} case impact(s)")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
