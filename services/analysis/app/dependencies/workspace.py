"""Authorize analysis resources against live workspace membership."""
import asyncio
from urllib.parse import quote
import httpx
from fastapi import HTTPException, Request
from sqlalchemy import text
from app.core.config import get_settings
from app.dependencies.auth import get_current_user
from app.infrastructure.db.session import async_session_factory


async def authorize_analysis_request(request: Request):
    if not request.url.path.startswith("/api/v1/"):
        return
    user = await asyncio.to_thread(get_current_user, request)
    workspace_ids = set()
    workspace_id = request.query_params.get("workspace_id")
    if workspace_id:
        workspace_ids.add(workspace_id)
    body = {}
    if "application/json" in request.headers.get("content-type", ""):
        try:
            body = await request.json()
        except ValueError:
            body = {}
        if isinstance(body, dict) and body.get("workspace_id"):
            workspace_ids.add(str(body["workspace_id"]))
    params = request.path_params
    job_id = params.get("job_id") or request.query_params.get("job_id")
    async with async_session_factory() as db:
        if job_id:
            workspace = await db.scalar(text("SELECT workspace_id FROM analysis.analysis_jobs WHERE id=CAST(:id AS uuid)"), {"id": str(job_id)})
            if workspace is None:
                raise HTTPException(status_code=404, detail="Job not found")
            workspace_ids.add(str(workspace))
        if params.get("repo_id"):
            rows = await db.execute(text("SELECT DISTINCT workspace_id FROM analysis.analysis_jobs WHERE repo_id=CAST(:id AS uuid)"), {"id": str(params["repo_id"])})
            workspace_ids.update(str(row[0]) for row in rows)
        if isinstance(body, dict) and body.get("finding_ids"):
            rows = await db.execute(text("SELECT DISTINCT workspace_id FROM analysis.analysis_results WHERE id::text=ANY(CAST(:ids AS text[]))"), {"ids": [str(v) for v in body["finding_ids"]]})
            workspace_ids.update(str(row[0]) for row in rows)
    cfg = get_settings()
    async with httpx.AsyncClient(timeout=10) as client:
        for workspace in workspace_ids:
            response = await client.get(f"http://core:8002/api/workspaces/{quote(workspace, safe='')}/",
                headers={"X-Internal-Request": cfg.jwt.internal_request_secret, "X-User-ID": user.sub})
            if response.status_code in (401, 403, 404):
                raise HTTPException(status_code=404, detail="Workspace not found")
            if response.is_error:
                raise HTTPException(status_code=503, detail="Workspace authorization unavailable")
