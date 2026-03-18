from cryptography.fernet import Fernet
from sqlalchemy import String, TypeDecorator

from app.config import get_settings


def _get_fernet() -> Fernet:
    key = get_settings().encryption_key
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY is not set. Generate one with: "
            "python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedString(TypeDecorator):
    """Transparently encrypts/decrypts string values stored in the database."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        fernet = _get_fernet()
        return fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        fernet = _get_fernet()
        return fernet.decrypt(value.encode("utf-8")).decode("utf-8")
