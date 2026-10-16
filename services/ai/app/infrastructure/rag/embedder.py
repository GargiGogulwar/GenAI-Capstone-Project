"""Local sentence embeddings; no hosted embedding API or second key."""
import asyncio
import threading
from app.core.config import settings

_models: dict[str, object] = {}
_lock = threading.Lock()

class Embedder:
    def __init__(self, provider: str | None = None, api_key: str | None = None):
        if provider and provider != "local":
            raise ValueError("Embeddings run locally in the Groq-only setup.")
        self.provider = "local"
        self.dimension = 384

    def _encode(self, texts: list[str]) -> list[list[float]]:
        from sentence_transformers import SentenceTransformer
        with _lock:
            if settings.embedding_model not in _models:
                _models[settings.embedding_model] = SentenceTransformer(settings.embedding_model, device="cpu")
            model = _models[settings.embedding_model]
        vectors = model.encode(texts, batch_size=16, normalize_embeddings=True).tolist()
        if vectors and len(vectors[0]) != self.dimension:
            raise ValueError("Use a 384-dimensional local embedding model for this database.")
        return vectors

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self._encode, texts) if texts else []