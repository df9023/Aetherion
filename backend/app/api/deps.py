from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings, Settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
) -> User:
    # Dev bypass: if DEBUG=true and dev headers present, use those
    if settings.debug:
        dev_user_id = request.headers.get("X-Dev-User-Id")
        if dev_user_id:
            result = await db.execute(select(User).where(User.id == UUID(dev_user_id)))
            user = result.scalar_one_or_none()
            if user and user.is_active:
                return user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_organization_id(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UUID:
    return current_user.organization_id


CurrentUser = Annotated[User, Depends(get_current_user)]
OrganizationId = Annotated[UUID, Depends(get_organization_id)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
