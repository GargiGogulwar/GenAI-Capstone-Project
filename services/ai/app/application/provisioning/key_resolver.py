"""Resolve the single server-side Groq key; never provision another provider."""
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.exceptions import InsufficientQuotaError

PROVIDER_FIELD_MAP = {"groq": "groq_key_encrypted"}
PROVIDER_URL_FIELD_MAP = {"groq": "groq_custom_url"}
_default_encrypter = Fernet(settings.key_encryption_key.encode()) if settings.key_encryption_key else None

def detect_provider_from_key(api_key: str) -> str | None:
    return "groq" if api_key.startswith("gsk_") else None

def _model_to_provider(model: str) -> str:
    return "groq"

async def resolve_provider_key(db_session=None, encrypter=None, user_id="", preferred_model=None):
    if not settings.groq_api_key:
        raise InsufficientQuotaError("Set GROQ_API_KEY in the server .env file.")
    return settings.groq_api_key, "groq", None

class KeyResolver:
    def __init__(self, encrypter=None):
        self.encrypter = encrypter or _default_encrypter

    async def resolve(self, user_id: str, preferred_model: str | None = None):
        return await resolve_provider_key(user_id=user_id, preferred_model=preferred_model)

    async def invalidate(self, user_id: str, preferred_model: str | None = None):
        return None
