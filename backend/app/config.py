from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Aetherion"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://aetherion:aetherion@localhost:5432/aetherion"

    # Auth (WorkOS)
    workos_api_key: str = ""
    workos_client_id: str = ""
    workos_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # URLs
    frontend_url: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    # Anthropic
    anthropic_api_key: str = ""

    # Embeddings
    voyage_api_key: str = ""
    openai_api_key: str = ""
    embedding_dimensions: int = 1536  # 1024 for Voyage, 1536 for OpenAI

    # Encryption
    encryption_key: str = ""  # Fernet key for PII encryption

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
