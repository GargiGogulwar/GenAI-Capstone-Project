"""Single provider policy. Model names are Groq IDs, not API providers."""

from app.core.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def models() -> list[str]:
    return list(dict.fromkeys([settings.groq_model, settings.groq_fast_model]))


def resolve_model(model: str | None) -> str:
    if model in models():
        return model
    # Preserve old saved conversations and the branded Krait option.
    if model == "groq-fast":
        return settings.groq_fast_model
    return settings.groq_model


def selector_models() -> list[dict]:
    return [
        {"id": model, "name": "Krait · Groq" if i == 0 else "Groq · Fast",
         "tier": "groq", "provider": "groq", "backendModel": model,
         "iconKey": "groq"}
        for i, model in enumerate(models())
    ]
