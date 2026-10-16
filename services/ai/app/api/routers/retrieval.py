"""Upload code/PDF/text, retrieve evidence, and inspect capstone capabilities."""
import hashlib
from pathlib import PurePosixPath
from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from app.api.dependencies.auth import JWTPayload, get_current_user
from app.api.dependencies.workspace import authorize_workspace
from app.core.config import settings
from app.infrastructure.rag.retrieval import RetrievalService

router = APIRouter(prefix="/v1/retrieval", tags=["retrieval"])
CurrentUser = Annotated[JWTPayload, Depends(get_current_user)]


class IndexDocument(BaseModel):
    workspace_id: str
    document_id: str = Field(min_length=1, max_length=300)
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=1_000_000)
    repo_id: str | None = None
    language: str = "text"


class RepositoryIndex(BaseModel):
    workspace_id: str
    repo_id: str
    documents: list[IndexDocument] = Field(max_length=200)


@router.post("/index-repository")
async def index_repository(body: RepositoryIndex, user: CurrentUser):
    await authorize_workspace(user, body.workspace_id)
    if any(d.workspace_id != body.workspace_id or d.repo_id != body.repo_id for d in body.documents):
        raise HTTPException(status_code=400, detail="Repository document scope mismatch")
    if sum(len(d.content) for d in body.documents) > 5_000_000:
        raise HTTPException(status_code=413, detail="Repository index batch exceeds 5 MB")
    count = 0
    for document in body.documents:
        count += await RetrievalService().index(**document.model_dump())
    return {"indexed_chunks": count, "indexed_files": len(body.documents)}


@router.post("/index")
async def index_document(body: IndexDocument, user: CurrentUser):
    await authorize_workspace(user, body.workspace_id)
    count = await RetrievalService().index(**body.model_dump())
    return {"indexed_chunks": count, "document_id": body.document_id}


@router.post("/upload")
async def upload_document(user: CurrentUser, workspace_id: str = Form(...), file: UploadFile = File(...)):
    await authorize_workspace(user, workspace_id)
    data = await file.read(5_000_001)
    if len(data) > 5_000_000:
        raise HTTPException(status_code=413, detail="Maximum upload size is 5 MB")
    name = PurePosixPath((file.filename or "document.txt").replace("\\", "/")).name
    extension = PurePosixPath(name).suffix.lower()
    if extension == ".pdf":
        import pymupdf
        try:
            with pymupdf.open(stream=data, filetype="pdf") as pdf:
                if pdf.page_count > 100:
                    raise HTTPException(status_code=413, detail="PDFs are limited to 100 pages")
                content = "\n\n".join(page.get_text() for page in pdf)
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Could not read PDF") from exc
    elif extension in {".txt", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".csv", ".yml", ".yaml", ".java", ".go", ".rs"}:
        try:
            content = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Text files must use UTF-8") from exc
    else:
        raise HTTPException(status_code=400, detail="Upload a PDF, text document, or source code file")
    if not content.strip() or len(content) > 1_000_000:
        raise HTTPException(status_code=400, detail="Document must contain 1–1,000,000 text characters")
    document_id = hashlib.sha256(name.encode()).hexdigest()
    count = await RetrievalService().index(workspace_id, document_id, name, content)
    return {"filename": name, "indexed_chunks": count, "document_id": document_id}


@router.get("/documents")
async def list_documents(user: CurrentUser, workspace_id: str):
    await authorize_workspace(user, workspace_id)
    return {"documents": await RetrievalService().list_documents(workspace_id)}


@router.get("/search")
async def search(user: CurrentUser, workspace_id: str, query: str = "", top_k: int = 6):
    await authorize_workspace(user, workspace_id)
    return {"sources": await RetrievalService().search(workspace_id, query, top_k=min(10, max(1, top_k)))}


@router.get("/capabilities")
async def capabilities(user: CurrentUser):
    return {"provider": "groq", "configured": bool(settings.groq_api_key),
            "model": settings.groq_model, "fast_model": settings.groq_fast_model,
            "embeddings": "local/all-MiniLM-L6-v2", "vector_store": "pgvector",
            "concepts": ["RAG", "overlapping chunks", "hybrid retrieval", "citations",
                         "structured outputs", "tool calling", "LangGraph agents",
                         "conversation memory", "token streaming", "evaluation"]}
