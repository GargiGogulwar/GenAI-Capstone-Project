"""Check current workspace membership through Core."""
from urllib.parse import quote
import httpx
from fastapi import HTTPException
from fastapi import Depends, Request
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.auth import JWTPayload
from app.core.config import settings


async def authorize_workspace(user: JWTPayload, workspace_id: str) -> None:
    if not user.sub or not workspace_id:
        raise HTTPException(status_code=403, detail="Workspace access required")
    headers = {"X-Internal-Request": settings.internal_request_secret, "X-User-ID": user.sub}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{settings.core_api_url}/workspaces/{quote(workspace_id, safe='')}/", headers=headers)
        if response.status_code in (401, 403, 404):
            raise HTTPException(status_code=404, detail="Workspace not found")
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Workspace authorization unavailable") from exc


async def authorize_knowledge_request(request: Request, user: JWTPayload = Depends(get_current_user)):
    workspace_id = request.path_params.get("workspace_id") or request.query_params.get("workspace_id")
    if request.method in {"POST", "PUT", "PATCH"} and "application/json" in request.headers.get("content-type", ""):
        body = await request.json()
        if isinstance(body, dict):
            workspace_id = body.get("workspace_id", workspace_id)
    if workspace_id:
        await authorize_workspace(user, str(workspace_id))
