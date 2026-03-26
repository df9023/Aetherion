import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.config import get_settings
from app.rate_limit import limiter

settings = get_settings()

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger("aetherion")

# ---------------------------------------------------------------------------
# Startup validation
# ---------------------------------------------------------------------------


def _validate_production_secrets() -> None:
    """Refuse to start in production with insecure defaults."""
    errors: list[str] = []
    if settings.jwt_secret_key == "change-me-in-production":
        errors.append(
            "JWT_SECRET_KEY is still the default value. "
            "Set a strong random secret before running in production."
        )
    if not settings.encryption_key:
        errors.append(
            "ENCRYPTION_KEY is empty. "
            "Generate a Fernet key and set it before running in production."
        )
    if errors:
        for e in errors:
            logger.critical(e)
        raise SystemExit(
            "FATAL: Refusing to start — insecure configuration detected.\n"
            + "\n".join(f"  - {e}" for e in errors)
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not settings.debug:
        _validate_production_secrets()
    logger.info("Aetherion API starting (debug=%s)", settings.debug)
    yield
    # Shutdown
    logger.info("Aetherion API shutting down")


app = FastAPI(
    title=settings.app_name,
    description="AI-native decision workspace for pension advisory",
    version="0.1.0",
    lifespan=lifespan,
)

# Attach limiter to app state (required by slowapi)
app.state.limiter = limiter


# ---------------------------------------------------------------------------
# Rate limit exceeded handler
# ---------------------------------------------------------------------------
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = getattr(exc, "retry_after", 60)
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": str(retry_after)},
    )


# ---------------------------------------------------------------------------
# Middleware: Security headers
# ---------------------------------------------------------------------------
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next) -> Response:
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Only add HSTS for non-localhost
    host = request.headers.get("host", "")
    if "localhost" not in host and "127.0.0.1" not in host:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


# ---------------------------------------------------------------------------
# Middleware: Request logging (non-PII)
# ---------------------------------------------------------------------------
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)

    # Extract user ID from auth (internal UUID, not PII)
    user_id = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from jose import jwt as _jwt

            token = auth_header.split(" ", 1)[1]
            payload = _jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")
        except Exception:
            pass
    if user_id is None and settings.debug:
        user_id = request.headers.get("X-Dev-User-Id")

    logger.info(
        '{"method":"%s","path":"%s","status":%d,"duration_ms":%.1f,"user_id":"%s"}',
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        user_id or "anonymous",
    )
    return response


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "Aetherion API", "version": "0.1.0"}
