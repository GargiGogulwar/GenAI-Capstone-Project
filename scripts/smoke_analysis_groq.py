"""Exercise real upload, report generation, scoped tools, and specialist review."""
import io
import json
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen
import zipfile

session = json.loads(Path(os.environ.get("CAPSTONE_SESSION", "tmp/capstone-session.json")).read_text())
container = bool(os.environ.get("CAPSTONE_CONTAINER"))
frontend = "http://frontend:3000" if container else "http://localhost:3000"
ai = frontend + "/api/ai"
analysis = frontend + "/analysis-api"
headers = {"Authorization": f"Bearer {session['access_token']}"}
if session.get("password"):
    request = Request(frontend + "/api/auth/signin/password/",
        data=json.dumps({"email": session["email"], "password": session["password"]}).encode(),
        headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=60) as response:
        headers["Authorization"] = "Bearer " + json.load(response)["access_token"]


def call(url, body=None, content_type="application/json"):
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    req = Request(url, data=data, headers={**headers, "Content-Type": content_type})
    with urlopen(req, timeout=240) as response:
        return json.load(response)


upload_boundary = "capstone-knowledge-upload"
upload_body = (f'--{upload_boundary}\r\nContent-Disposition: form-data; name="workspace_id"\r\n\r\n'
    f'{session["workspace_id"]}\r\n--{upload_boundary}\r\n'
    'Content-Disposition: form-data; name="file"; filename="capstone-notes.md"\r\n'
    'Content-Type: text/markdown\r\n\r\n# Capstone notes\nThe demo release is called Aurora.\r\n'
    f'--{upload_boundary}--\r\n').encode()
uploaded = call(ai + "/v1/retrieval/upload", upload_body, f"multipart/form-data; boundary={upload_boundary}")
assert uploaded["indexed_chunks"] > 0, uploaded
print("PASS: frontend multipart document upload -> indexed knowledge", flush=True)

archive = io.BytesIO()
with zipfile.ZipFile(archive, "w") as z:
    z.writestr("app.py", '''import sqlite3

def find_user(name):
    connection = sqlite3.connect("users.db")
    return connection.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchall()
''')
    z.writestr("README.md", "# Atlas demo\nAtlas service owner is Priya. The service uses SQLite.\n")
boundary = "kraivor-capstone-upload"
body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="atlas.zip"\r\n'
        'Content-Type: application/zip\r\n\r\n').encode() + archive.getvalue() + f"\r\n--{boundary}--\r\n".encode()
job = call(analysis + f"/api/v1/files/upload?workspace_id={session['workspace_id']}", body,
           f"multipart/form-data; boundary={boundary}")
job_id = job["job_id"]
Path("/tmp/analysis-smoke-job.json" if container else "tmp/analysis-smoke-job.json").write_text(json.dumps(job))
print("PASS: authenticated ZIP upload creates analysis job", job_id, flush=True)
deadline = time.monotonic() + 480
previous = None
while time.monotonic() < deadline:
    job = call(analysis + f"/api/v1/jobs/{job_id}")
    status = (job["status"], job.get("progress_message"))
    if status != previous:
        print("Analysis:", *status, flush=True)
        previous = status
    if job["status"] in {"completed", "failed", "cancelled"}:
        break
    time.sleep(4)
assert job["status"] == "completed", job
report = call(analysis + f"/api/v1/reports/by-job/{job_id}")
assert report["total_files"] >= 1 and report["overall_score"] is not None, report
print("PASS: analysis pipeline -> persisted report and scores", flush=True)
guide = call(analysis + f"/api/v1/enterprise-guide?job_id={job_id}")
assert guide and guide.get("ai_executive_summary"), guide
findings = call(analysis + f"/api/v1/findings?job_id={job_id}")
assert any(f.get("is_ai_enriched") and f.get("ai_explanation") for f in findings["findings"]), findings
print("PASS: Groq executive summary and enriched findings saved in report", flush=True)
evidence = call(ai + f"/v1/retrieval/search?workspace_id={session['workspace_id']}&query=Atlas%20service%20owner")
assert any("Priya" in source["content"] for source in evidence["sources"]), evidence
print("PASS: analyzed source files available in hybrid retrieval", flush=True)
review = call(ai + "/v1/chat", {"workspace_id": session["workspace_id"], "stream": False, "mode": "research",
    "message": "Review Atlas find_user for security vulnerabilities. Cite the code and suggest a safe fix."})
assert any(word in review["content"].lower() for word in ("injection", "parameter", "concatenat")), review
assert any(step in review.get("trace", []) for step in ("security", "code")), review
print("PASS: specialist review -> grounded Groq synthesis", flush=True)
tools = call(ai + "/v1/chat", {"workspace_id": session["workspace_id"], "stream": False,
    "message": "Use the workspace tool to list the projects in this workspace."})
assert tools["content"] and "get_workspace_projects" in tools.get("trace", []), tools
print("PASS: workspace tool workflow returns a response", flush=True)
Path("/tmp/groq-analysis-results.json" if container else "tmp/groq-analysis-results.json").write_text(
    json.dumps({"job_id": job_id, "status": job["status"], "score": report["overall_score"],
                "review_trace": review.get("trace"), "tool_trace": tools.get("trace")}, indent=2))
