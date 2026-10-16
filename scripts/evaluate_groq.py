"""Small reproducible RAG evaluation; every generation uses Groq.

Requires tmp/capstone-session.json from the integration fixture, or an equivalent
local JSON file containing access_token and workspace_id. Never prints secrets.
"""
import argparse
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://localhost:8004")
parser.add_argument("--session", default="tmp/capstone-session.json")
args = parser.parse_args()
session = json.loads(Path(args.session).read_text())
cases = [
    {"question": "What is Orion's database connection pool limit?", "expected": "12"},
    {"question": "Who owns Orion incident response?", "expected": "Mira"},
    {"question": "Which region hosts Orion?", "expected": "eu-west-2"},
]
results = []
for case in cases:
    start = time.monotonic()
    body = {"workspace_id": session["workspace_id"], "message": case["question"], "stream": False}
    request = Request(args.base_url + "/v1/chat", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {session['access_token']}", "Content-Type": "application/json"})
    with urlopen(request, timeout=180) as response:
        answer = json.load(response)
    citations = re.findall(r"\[S(\d+)\]", answer["content"])
    sources = answer.get("sources") or []
    results.append({"question": case["question"],
        "answer_contains_expected_fact": case["expected"].lower() in answer["content"].lower().translate(str.maketrans({"‑": "-", "–": "-"})),
        "has_citation": bool(citations),
        "citation_ids_valid": bool(citations) and all(1 <= int(c) <= len(sources) for c in citations),
        "retrieval_contains_expected_fact": any(case["expected"].lower() in s["content"].lower() for s in sources),
        "latency_seconds": round(time.monotonic() - start, 2)})
report = {"cases": results, "note": "Fact containment and citation checks are proxies, not a guarantee of factual correctness."}
Path("tmp/groq-evaluation.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
raise SystemExit(0 if all(all(c[k] for k in ("answer_contains_expected_fact", "has_citation", "citation_ids_valid", "retrieval_contains_expected_fact")) for c in results) else 1)
