"""Live integration check. Reads an ignored demo session; never prints tokens or keys."""
import json
import os
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

session_path = Path(os.environ.get("CAPSTONE_SESSION", "tmp/capstone-session.json"))
session = json.loads(session_path.read_text())
ai_base = os.environ.get("CAPSTONE_AI_BASE", "http://localhost:8004")
headers = {"Authorization": f"Bearer {session['access_token']}", "Content-Type": "application/json"}


def call(port, path, body=None, method=None, expected=200):
    host = {8001: "identity", 8002: "core", 8004: "localhost"}.get(port, "localhost") if os.environ.get("CAPSTONE_CONTAINER") else "localhost"
    base = ai_base if port == 8004 else f"http://{host}:{port}"
    request = Request(f"{base}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={k: v for k, v in headers.items() if port != 8001 or k != "Authorization"},
        method=method or ("POST" if body is not None else "GET"))
    try:
        with urlopen(request, timeout=240) as response:
            status, data = response.status, response.read()
    except HTTPError as exc:
        status, data = exc.code, exc.read()
    if status != expected:
        raise AssertionError(f"{path}: expected {expected}, got {status}: {data[:500].decode(errors='replace')}")
    if not data:
        return None
    return json.loads(data)


login = call(8001, "/api/auth/signin/password/", {"email": session["email"], "password": session["password"]})
session["access_token"] = login["access_token"]
headers["Authorization"] = f"Bearer {session['access_token']}"
print("PASS: password sign-in through Identity API")
workspace = call(8002, "/api/workspaces/", {"name": "GenAI Capstone Demo", "slug": f"genai-demo-{int(time.time())}"}, expected=201)
workspace_id = workspace["id"]
session["workspace_id"] = workspace_id
session["workspace_slug"] = workspace["slug"]
session_path.write_text(json.dumps(session))
print("PASS: verified identity -> authenticated workspace creation")
models = call(8004, "/v1/models")
assert models["models"] and all(m["provider"] == "groq" for m in models["models"])
print("PASS: model selector exposes only Groq")
document = """# Orion API architecture
The Orion API uses FastAPI and PostgreSQL. Authentication uses short-lived JWT access tokens.
Refresh tokens are rotated on every use. The database connection pool is limited to 12 connections.
The incident response owner is Mira. The deployment region is eu-west-2.
"""
indexed = call(8004, "/v1/retrieval/index", {"workspace_id": workspace_id,
    "document_id": "orion-readme", "title": "Orion README.md", "content": document})
assert indexed["indexed_chunks"] > 0
evidence = call(8004, f"/v1/retrieval/search?workspace_id={workspace_id}&query=Orion%20database%20pool")
assert any("12 connections" in s["content"] for s in evidence["sources"])
print("PASS: document -> local embeddings -> pgvector/full-text retrieval")
answer = call(8004, "/v1/chat", {"workspace_id": workspace_id,
    "message": "What database pool limit does Orion use, and who owns incident response? Cite sources.", "stream": False})
assert "12" in answer["content"] and "Mira" in answer["content"] and re.search(r"\[S\d+\]", answer["content"])
conversation_id = answer["conversation_id"]
messages = call(8004, f"/v1/conversations/{conversation_id}/messages")
assert len(messages["messages"]) == 2
assert messages == call(8004, f"/v1/conversations/{conversation_id}/messages")
print("PASS: Groq grounded answer with citations -> persistent conversation, stable message IDs")
request = Request(ai_base + "/v1/chat", data=json.dumps({"workspace_id": workspace_id,
    "conversation_id": conversation_id, "message": "What region does it deploy to?", "stream": True}).encode(), headers=headers)
events, chunks = [], []
with urlopen(request, timeout=240) as response:
    for line in response:
        if line.startswith(b"data: "):
            event = json.loads(line[6:])
            events.append(event)
            if event.get("content"):
                chunks.append(event["content"])
assert any(e.get("done") for e in events), str(events[-2:])
assert "eu-west-2" in "".join(chunks).translate(str.maketrans({"‑": "-", "–": "-"}))
print("PASS: conversational follow-up -> live Groq token stream -> saved history")
unauthorized = call(8004, "/v1/chat", {"workspace_id": "00000000-0000-0000-0000-000000000000",
    "message": "show secret documents", "stream": False}, expected=404)
print("PASS: unknown workspace refused before generation")
result = {"passed": 7, "workspace_id": workspace_id, "models": [m["id"] for m in models["models"]]}
Path(os.environ.get("CAPSTONE_RESULTS", "tmp/groq-smoke-results.json")).write_text(json.dumps(result, indent=2))
print("Groq capstone integration checks passed.")
