"""Test infrastructure for Aetherion API tests.

Uses a separate PostgreSQL test database (aetherion_test) with full schema.
Each test commits its setup data (so the ASGI app can see it on a separate
connection), then cleans up at the end by deleting in reverse FK order.

Existing sync unit tests (suitability, pension_calculator, eligibility) remain
unaffected — they don't use any of these fixtures.
"""

import os
import sys
import uuid
from pathlib import Path
from collections.abc import AsyncGenerator

# Ensure backend package is importable (needed for sync tests too)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set test environment BEFORE any app imports
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://aetherion:password@localhost:5432/aetherion_test",
)
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Clear cached settings so test env vars take effect
from app.config import get_settings

get_settings.cache_clear()

# Generate a proper Fernet key for encryption
from cryptography.fernet import Fernet

os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
get_settings.cache_clear()

from app.database import Base, get_db
from app.api.deps import get_current_user
from app.main import app
from app.models import Organization, User
from app.models.base import OrganizationType, UserRole

# ---------------------------------------------------------------------------
# Test database engine
# ---------------------------------------------------------------------------

TEST_DB_URL = os.environ["DATABASE_URL"]

test_engine = create_async_engine(TEST_DB_URL, echo=False, pool_size=5)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# Table names in reverse FK dependency order for cleanup
_CLEANUP_TABLES = [
    "evidences",
    "documents",
    "recommendations",
    "case_impacts",
    "regulatory_changes",
    "firm_insights",
    "audit_entries",
    "workflows",
    "cases",
    "clients",
    "client_organizations",
    "knowledge_items",
    "users",
    "organizations",
]

# ---------------------------------------------------------------------------
# One-time table creation (no session-scoped async fixtures needed)
# ---------------------------------------------------------------------------

_tables_created = False


# ---------------------------------------------------------------------------
# Per-test: session + cleanup
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession. Creates tables on first use, truncates after test."""
    global _tables_created
    if not _tables_created:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        _tables_created = True

    session = TestSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        # Clean up all data after each test
        async with test_engine.begin() as conn:
            for table in _CLEANUP_TABLES:
                await conn.execute(text(f"DELETE FROM {table}"))


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Test Org AB",
        org_type=OrganizationType.ADVISORY_FIRM,
        jurisdiction="SE",
        settings={},
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        email=f"test-{uuid.uuid4().hex[:8]}@testorg.se",
        name="Erik Testsson",
        role=UserRole.ADVISOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def second_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Other Org AB",
        org_type=OrganizationType.PENSION_PROVIDER,
        jurisdiction="SE",
        settings={},
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest_asyncio.fixture
async def second_user(db_session: AsyncSession, second_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        organization_id=second_org.id,
        email=f"other-{uuid.uuid4().hex[:8]}@otherorg.se",
        name="Anna Annansson",
        role=UserRole.ADVISOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def reviewer_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        email=f"reviewer-{uuid.uuid4().hex[:8]}@testorg.se",
        name="Sara Reviewersson",
        role=UserRole.COMPLIANCE_REVIEWER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


# ---------------------------------------------------------------------------
# HTTP client fixtures
#
# Only get_db is overridden (once). Authentication uses the dev bypass
# (X-Dev-User-Id header) so multiple clients with different users can
# coexist in the same test without conflicting on dependency_overrides.
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def _app_db_override():
    """Set up the DB override for the ASGI app once per test."""

    async def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(test_user: User, _app_db_override) -> AsyncGenerator[AsyncClient, None]:
    """httpx.AsyncClient wired to the test app, authenticated as test_user."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-Dev-User-Id": str(test_user.id)},
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def client_org2(second_user: User, _app_db_override) -> AsyncGenerator[AsyncClient, None]:
    """httpx.AsyncClient authenticated as the second org's user."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-Dev-User-Id": str(second_user.id)},
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def reviewer_client(reviewer_user: User, _app_db_override) -> AsyncGenerator[AsyncClient, None]:
    """httpx.AsyncClient authenticated as the compliance reviewer."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-Dev-User-Id": str(reviewer_user.id)},
    ) as ac:
        yield ac
