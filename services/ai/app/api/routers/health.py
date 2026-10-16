import logging
import time

from fastapi import APIRouter

from app.api.dependencies.backpressure import get_backpressure_stats
from app.api.schemas.health import HealthResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@router.get("/health/ready", response_model=HealthResponse)
async def readiness():
    from app.infrastructure.db.database import async_session_factory
    from app.infrastructure.cache.redis_client import get_redis
    from sqlalchemy import text
    from fastapi import HTTPException
    try:
        async with async_session_factory() as db:
            await db.execute(text("SELECT 1 FROM ai.conversations LIMIT 1"))
        await (await get_redis()).ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="AI dependencies unavailable") from exc
    if not settings.groq_api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured")
    return HealthResponse()


@router.get("/health/load")
async def load_stats():
    return get_backpressure_stats()


@router.get("/health/providers")
async def provider_health():
    """Check connectivity to all configured LLM providers.

    Inspired by Claw-code's /doctor command — tests each provider with a minimal
    request and reports status + latency.
    """
    results = {}
    providers_to_check = []

    if settings.groq_api_key:
        providers_to_check.append(("groq", settings.groq_api_key, "groq", settings.groq_fast_model))

    for name, api_key, provider, model in providers_to_check:
        start = time.monotonic()
        try:
            from app.infrastructure.llm.client import LLMClient
            client = LLMClient(api_key=api_key, provider=provider, model=model)
            await client.generate(
                [{"role": "user", "content": "ping"}],
                max_tokens=5,
                timeout=15.0,
            )
            elapsed = int((time.monotonic() - start) * 1000)
            results[name] = {
                "status": "healthy",
                "latency_ms": elapsed,
                "model": model,
            }
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            results[name] = {
                "status": "unhealthy",
                "error": str(e)[:200],
                "latency_ms": elapsed,
                "model": model,
            }

    return {"providers": results}
