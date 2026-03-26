from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_user_id_or_ip(request: Request) -> str:
    """Use authenticated user ID for rate-limit key when available, else IP."""
    from app.config import get_settings

    settings = get_settings()

    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from jose import jwt as _jwt

            token = auth_header.split(" ", 1)[1]
            payload = _jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass
    # Dev bypass
    dev_user = request.headers.get("X-Dev-User-Id")
    if dev_user and settings.debug:
        return f"user:{dev_user}"
    return get_remote_address(request)


limiter = Limiter(key_func=_get_user_id_or_ip, default_limits=["100/minute"])
