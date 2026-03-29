# Task: Build test infrastructure + API endpoint tests

Read `CLAUDE.md` for project context. Read `backend/tests/` to see the existing deterministic tests and `conftest.py`. Read `backend/app/api/v1/endpoints/` for all endpoint files, `backend/app/schemas/` for request/response models, and `backend/app/models/` for SQLAlchemy models.

## 1. Test infrastructure

### Update `conftest.py`

Replace the minimal conftest with a full async test setup:

```python
import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.base import Base
from app.models import Organization, User

# Use a separate test database — falls back to in-memory SQLite if TEST_DATABASE_URL not set
import os
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

Key fixtures to create:

- `@pytest.fixture(scope="session") def event_loop()` — single event loop for all tests
- `@pytest_asyncio.fixture(scope="session") async def setup_database()` — create all tables once, drop after session
- `@pytest_asyncio.fixture async def db_session(setup_database)` — per-test session with rollback (use `begin_nested` + rollback for isolation)
- `@pytest_asyncio.fixture async def test_org(db_session)` — create a test Organization
- `@pytest_asyncio.fixture async def test_user(db_session, test_org)` — create a test User in that org
- `@pytest_asyncio.fixture async def second_org(db_session)` — second org for multi-tenancy tests
- `@pytest_asyncio.fixture async def second_user(db_session, second_org)` — user in second org
- `@pytest_asyncio.fixture async def client(db_session, test_user)` — `httpx.AsyncClient` with app, overriding `get_db` and `get_current_user` dependencies
- `@pytest_asyncio.fixture async def client_org2(db_session, second_user)` — client authenticated as second org user

The auth override should inject the test user without hitting WorkOS/JWT:
```python
async def override_get_current_user():
    return test_user

app.dependency_overrides[get_current_user] = override_get_current_user
```

### Add `aiosqlite` to requirements.txt

Add `aiosqlite>=0.20.0` under the Testing section in `backend/requirements.txt`.

Also add `factory-boy>=3.3.0` if you use factories (optional — simple helper functions are fine too).

### Important: keep existing tests working

The 3 existing test files (`test_suitability.py`, `test_pension_calculator.py`, `test_eligibility.py`) are pure sync unit tests. They must still pass. Don't break them.

## 2. Factory helpers

Create `backend/tests/factories.py` with simple async helper functions (not factory-boy, just plain functions):

```python
async def create_client(db: AsyncSession, org_id: str, **overrides) -> Client:
    """Create a test client with sensible defaults."""
    defaults = {
        "id": str(uuid.uuid4()),
        "name": "Test Testsson",
        "date_of_birth": "1970-01-15",
        "employment_status": "employed",
        "collective_agreement": "ITP1",
        "organization_id": org_id,
        "created_by": "test-user",
        ...
    }
    defaults.update(overrides)
    client = Client(**defaults)
    db.add(client)
    await db.flush()
    return client

async def create_case(db: AsyncSession, org_id: str, client_id: str, **overrides) -> Case: ...
async def create_knowledge_item(db: AsyncSession, org_id: str, **overrides) -> KnowledgeItem: ...
```

## 3. API endpoint tests

Create one test file per endpoint module. All tests are `async def` using `pytest.mark.asyncio`.

### `test_health.py`
- `test_health_returns_200` — GET `/api/v1/health` returns 200 with status "healthy"

### `test_cases.py`
- `test_create_case` — POST creates a case, returns 201 with correct fields
- `test_list_cases` — GET returns list scoped to org
- `test_get_case` — GET by ID returns the case
- `test_get_case_not_found` — GET nonexistent ID returns 404
- `test_update_case_status` — PATCH updates status
- `test_invalid_status_transition` — PATCH with invalid status returns 422 or 400
- `test_org_isolation_cases` — client_org2 cannot see org1's cases (returns empty list or 404)

### `test_clients.py`
- `test_create_client` — POST creates client, returns 201
- `test_list_clients` — GET returns org-scoped list
- `test_get_client` — GET by ID returns the client
- `test_get_client_not_found` — GET nonexistent ID returns 404
- `test_search_clients` — GET with search query filters results
- `test_org_isolation_clients` — org2 cannot see org1's clients

### `test_knowledge.py`
- `test_create_knowledge_item` — POST creates item, returns 201
- `test_list_knowledge_items` — GET returns org-scoped list
- `test_get_knowledge_item` — GET by ID returns the item
- `test_search_knowledge` — GET with query param returns filtered results
- `test_org_isolation_knowledge` — org2 cannot see org1's items

### `test_recommendations.py`
- `test_get_recommendation_not_found` — GET nonexistent returns 404
- `test_get_evidence` — GET `/{id}/evidence` returns evidence list
- Skip the `generate` endpoint test (requires LLM mock — save for later)

### `test_dashboard.py`
- `test_recent_audit` — GET `/api/v1/audit/recent` returns recent entries
- `test_recent_audit_respects_limit` — limit param works
- `test_recent_audit_org_isolation` — org2 doesn't see org1's audit entries

### `test_auth.py`
- `test_unauthenticated_request_rejected` — request without auth override returns 401/403
- Skip WorkOS-specific tests for now

## 4. Running tests

After creating all files, run `pytest backend/tests/ -v --tb=short` and fix any failures. 

If SQLite doesn't support certain PostgreSQL-specific features (like pgvector, custom enums), handle gracefully:
- For enum columns: use `String` type in SQLite fallback or mock the enum
- For pgvector: skip vector-related tests with `pytest.mark.skipif`
- The goal is: all non-vector, non-enum tests pass with SQLite; full suite passes with PostgreSQL

## Important

- Every test file must be independent — no test depends on another test's side effects
- Use `await db_session.rollback()` or nested transactions for isolation
- Don't test LLM calls — mock them or skip those tests for now
- Don't test document generation (PDF/DOCX) — that requires file system setup
- Focus on CRUD operations, org isolation, and input validation
- All tests should run in under 10 seconds total (no real I/O)
