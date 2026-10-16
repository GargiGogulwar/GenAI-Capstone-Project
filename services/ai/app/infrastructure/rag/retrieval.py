"""Tenant-scoped chunk ingestion and hybrid pgvector/full-text retrieval."""

import hashlib
from sqlalchemy import text
from app.infrastructure.db.database import async_session_factory
from app.infrastructure.rag.embedder import Embedder


def chunk_document(content: str, size: int = 1700, overlap: int = 200) -> list[dict]:
    if size <= overlap or overlap < 0:
        raise ValueError("Chunk overlap must be smaller than chunk size.")
    chunks, start = [], 0
    while start < len(content):
        end = min(start + size, len(content))
        if end < len(content):
            boundary = content.rfind("\n", start + size // 2, end)
            if boundary > start:
                end = boundary + 1
        value = content[start:end]
        if value.strip():
            chunks.append({"content": value, "line_start": content.count("\n", 0, start) + 1,
                           "line_end": content.count("\n", 0, end) + 1})
        if end == len(content):
            break
        start = max(start + 1, end - overlap)
    return chunks


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(float(v)) for v in vector) + "]"


class RetrievalService:
    async def list_documents(self, workspace_id: str) -> list[dict]:
        async with async_session_factory() as db:
            rows = (await db.execute(text("""
                SELECT repo_id, file_path, COUNT(*) AS indexed_chunks
                FROM ai.code_embeddings
                WHERE workspace_id=:ws AND repo_id LIKE 'knowledge:%'
                GROUP BY repo_id, file_path ORDER BY file_path, repo_id
                LIMIT 1000
            """), {"ws": workspace_id})).mappings().all()
        return [{"document_id": row["repo_id"].removeprefix("knowledge:"),
                 "filename": row["file_path"], "indexed_chunks": row["indexed_chunks"]}
                for row in rows]

    async def index(self, workspace_id: str, document_id: str, title: str, content: str,
                    repo_id: str | None = None, language: str = "text") -> int:
        chunks = chunk_document(content)
        vectors = await Embedder().embed_batch([c["content"] for c in chunks])
        namespace = repo_id or f"knowledge:{document_id}"
        prefix = hashlib.sha256(f"{workspace_id}:{namespace}:{document_id}".encode()).hexdigest()
        async with async_session_factory() as db:
            await db.execute(text("DELETE FROM ai.code_embeddings WHERE workspace_id=:ws AND id LIKE :prefix"),
                             {"ws": workspace_id, "prefix": prefix + ":%"})
            for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
                await db.execute(text("""
                    INSERT INTO ai.code_embeddings
                    (id, repo_id, workspace_id, file_path, language, content, embedding, line_start, line_end)
                    VALUES (:id, :repo, :ws, :path, :lang, :content, CAST(:vector AS vector), :start, :end)
                """), {"id": f"{prefix}:{i}", "repo": namespace, "ws": workspace_id,
                       "path": title, "lang": language, "content": chunk["content"],
                       "vector": vector_literal(vector), "start": chunk["line_start"], "end": chunk["line_end"]})
            await db.commit()
        return len(chunks)

    async def search(self, workspace_id: str, query: str, repo_ids: list[str] | None = None,
                     top_k: int = 6) -> list[dict]:
        if not workspace_id:
            return []
        async with async_session_factory() as db:
            count = await db.scalar(text("SELECT COUNT(*) FROM ai.code_embeddings WHERE workspace_id=:ws"), {"ws": workspace_id})
        if not count:
            return []
        vector = vector_literal(await Embedder().embed(query))
        params = {"ws": workspace_id, "query": query, "vector": vector, "limit": top_k * 3,
                  "repos": repo_ids or []}
        scope = "workspace_id=:ws AND (cardinality(CAST(:repos AS text[]))=0 OR repo_id=ANY(CAST(:repos AS text[])) OR repo_id LIKE 'knowledge:%')"
        async with async_session_factory() as db:
            semantic = (await db.execute(text(
                "SELECT id, file_path, content, repo_id, line_start, line_end, "
                "1-(embedding <=> CAST(:vector AS vector)) AS similarity FROM ai.code_embeddings WHERE "
                + scope + " AND embedding IS NOT NULL ORDER BY embedding <=> CAST(:vector AS vector) LIMIT :limit"
            ), params)).mappings().all()
            lexical = (await db.execute(text(
                "SELECT id, file_path, content, repo_id, line_start, line_end FROM ai.code_embeddings WHERE "
                + scope + " AND to_tsvector('english',content) @@ plainto_tsquery('english',:query) "
                "ORDER BY ts_rank_cd(to_tsvector('english',content),plainto_tsquery('english',:query)) DESC LIMIT :limit"
            ), params)).mappings().all()
        fused = {}
        for results in (semantic, lexical):
            for rank, row in enumerate(results, 1):
                item = fused.setdefault(row["id"], {**dict(row), "score": 0.0})
                item["score"] += 1 / (60 + rank)
        return sorted(fused.values(), key=lambda x: x["score"], reverse=True)[:top_k]
