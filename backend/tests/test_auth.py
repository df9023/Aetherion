"""Tests for authentication behavior.

Tests that unauthenticated requests are rejected when no auth override is in place.
Skips WorkOS-specific tests for now.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import get_db


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(db_session):
    """Request without auth override should return 401.

    We override get_db (so the DB works) but NOT get_current_user,
    so the auth dependency runs and rejects the request.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # Deliberately NOT overriding get_current_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            resp = await ac.get("/api/v1/cases")
            assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unauthenticated_health_still_works(db_session):
    """Health endpoint does not require auth — should work without credentials."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            resp = await ac.get("/api/v1/health")
            assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()
