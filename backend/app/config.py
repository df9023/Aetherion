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
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Anthropic
    anthropic_api_key: str = ""

    # OpenAI (embeddings)
    openai_api_key: str = ""

    # Encryption
    encryption_key: str = ""  # Fernet key for PII encryption

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
