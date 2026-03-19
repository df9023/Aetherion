"""
Seed script for Aetherion development database.

Populates:
- 1 organization (fictional Swedish advisory firm)
- 2 users (admin + advisor)
- 2 clients with realistic Swedish pension situations
- 1 case per client
- Knowledge items with embeddings for RAG retrieval

Usage:
    cd backend
    source .venv/bin/activate
    python -m scripts.seed
"""

import asyncio
import hashlib
import sys
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

# Ensure the backend package is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session_maker, engine
from app.models.organization import Organization
from app.models.user import User
from app.models.client import Client
from app.models.case import Case
from app.models.audit_entry import AuditEntry
from app.models.knowledge_item import KnowledgeItem
from app.models.base import (
    OrganizationType,
    UserRole,
    EmploymentStatus,
    CollectiveAgreement,
    RiskProfile,
    CaseType,
    CaseStatus,
    KnowledgeCategory,
    AuditAction,
    ActorType,
)


# ---------------------------------------------------------------------------
# Deterministic UUIDs (reproducible seeds)
# ---------------------------------------------------------------------------
def _uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_DNS, f"aetherion.seed.{name}")


ORG_ID = _uuid("org.nordenra")
USER_ADMIN_ID = _uuid("user.admin.eriksson")
USER_ADVISOR_ID = _uuid("user.advisor.lindqvist")
CLIENT_1_ID = _uuid("client.anna.johansson")
CLIENT_2_ID = _uuid("client.lars.pettersson")
CASE_1_ID = _uuid("case.anna.retirement")
CASE_2_ID = _uuid("case.lars.lonvaxling")

KI_IDS = [_uuid(f"knowledge.{i}") for i in range(6)]


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
        "source": "NordPension Rådgivning — Intern policy 2024-01",
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
        "source": "NordPension Rådgivning — Riskprofilsguide v3",
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
            await db.execute(text("DELETE FROM audit_entries"))
            await db.execute(text("DELETE FROM evidences"))
            await db.execute(text("DELETE FROM workflows"))
            await db.execute(text("DELETE FROM documents"))
            await db.execute(text("DELETE FROM recommendations"))
            await db.execute(text("DELETE FROM cases"))
            await db.execute(text("DELETE FROM clients"))
            await db.execute(text("DELETE FROM knowledge_items"))
            await db.execute(text("DELETE FROM users"))
            await db.execute(text("DELETE FROM organizations"))
            await db.commit()

        print("Seeding organization...")
        org = Organization(
            id=ORG_ID,
            name="NordPension Rådgivning AB",
            org_type=OrganizationType.ADVISORY_FIRM,
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
            email="erik.eriksson@nordpension.se",
            name="Erik Eriksson",
            role=UserRole.ADMIN,
            workos_user_id="workos_dev_admin_001",
        )
        advisor = User(
            id=USER_ADVISOR_ID,
            organization_id=ORG_ID,
            email="maria.lindqvist@nordpension.se",
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
        for ki_data in KNOWLEDGE_ITEMS:
            embedding = fake_embedding(ki_data["content"])
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
        await db.commit()

        print()
        print("=" * 60)
        print("Seed complete!")
        print("=" * 60)
        print(f"Organization:  {ORG_ID}  NordPension Rådgivning AB")
        print(f"Admin user:    {USER_ADMIN_ID}  erik.eriksson@nordpension.se")
        print(f"Advisor user:  {USER_ADVISOR_ID}  maria.lindqvist@nordpension.se")
        print(f"Client 1:      {CLIENT_1_ID}  Anna Johansson (ITP1, 45 yr)")
        print(f"Client 2:      {CLIENT_2_ID}  Lars Pettersson (ITP2, 58 yr)")
        print(f"Case 1:        {CASE_1_ID}  Retirement planning")
        print(f"Case 2:        {CASE_2_ID}  Löneväxling")
        print(f"Knowledge:     {len(KNOWLEDGE_ITEMS)} items with embeddings")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
