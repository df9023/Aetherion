from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from jose import jwt
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import workos

from app.config import get_settings, Settings
from app.database import get_db
from app.api.deps import CurrentUser
from app.models.user import User
from app.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    organization_id: str


def _create_access_token(user: User, settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user.id),
        "org": str(user.organization_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@router.get("/login")
@limiter.limit("20/minute", key_func=get_remote_address)
async def login(
    request: Request,
    settings: Settings = Depends(get_settings),
    redirect_uri: str | None = None,
) -> RedirectResponse:
    """Redirect to WorkOS AuthKit login page."""
    if not settings.workos_api_key or not settings.workos_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WorkOS is not configured. Set WORKOS_API_KEY and WORKOS_CLIENT_ID.",
        )

    client = workos.WorkOS(
        api_key=settings.workos_api_key,
    )
    authorization_url = client.sso.get_authorization_url(
        redirect_uri=redirect_uri or settings.workos_redirect_uri,
        client_id=settings.workos_client_id,
    )
    return RedirectResponse(url=authorization_url, status_code=302)


@router.get("/callback")
@limiter.limit("20/minute", key_func=get_remote_address)
async def callback(
    request: Request,
    code: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RedirectResponse:
    """WorkOS redirects here after login. Exchange code for profile, issue JWT."""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code.",
        )

    try:
        client = workos.WorkOS(
            api_key=settings.workos_api_key,
        )
        profile_and_token = client.sso.get_profile_and_token(code)
        profile = profile_and_token.profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"WorkOS authentication failed: {e}",
        )

    # Find user by email — we don't auto-create accounts
    result = await db.execute(
        select(User).where(User.email == profile.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No account found for this email. Contact your administrator.",
        )

    # Update WorkOS user ID and last active timestamp
    user.workos_user_id = profile.id
    user.last_active_at = datetime.now(timezone.utc)
    await db.flush()

    token = _create_access_token(user, settings)

    # Redirect to frontend with token
    redirect_url = f"{settings.frontend_url}/auth/callback?token={token}"
    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/logout")
async def logout() -> dict:
    """Logout endpoint. With pure JWT auth, the client just discards the token."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfile)
async def me(current_user: CurrentUser) -> UserProfile:
    """Return the current authenticated user's profile."""
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        organization_id=str(current_user.organization_id),
    )
