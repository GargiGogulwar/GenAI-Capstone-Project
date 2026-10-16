"""Local-only sign-up/email verification check using MailHog, without printing credentials."""
import json
import os
import re
import secrets
from email import message_from_string
from urllib.parse import urlencode, unquote
from urllib.request import Request, urlopen

inside = bool(os.environ.get("CAPSTONE_CONTAINER"))
base = os.environ.get("CAPSTONE_BASE_URL") or ("http://frontend:3000" if inside else "http://localhost:3000")
mail = "http://mailhog:8025" if inside else "http://localhost:8025"
email = f"signup-{secrets.token_hex(5)}@example.test"
password = secrets.token_urlsafe(24)


def post(path, body):
    with urlopen(Request(base + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}), timeout=60) as response:
        return json.load(response)


signup = post("/api/auth/signup/", {"email": email, "name": "Capstone signup check",
    "password": password, "password_confirm": password})
assert signup["email_sent"], "Local verification email was not delivered"
with urlopen(mail + "/api/v2/search?" + urlencode({"kind": "to", "query": email}), timeout=30) as response:
    messages = json.load(response)
assert messages["items"], "MailHog did not receive the test verification message"
item = messages["items"][0]
message = message_from_string(item.get("Raw", {}).get("Data") or item["Content"]["Body"])
body = "\n".join((part.get_payload(decode=True) or b"").decode(part.get_content_charset() or "utf-8", errors="replace")
                 for part in message.walk() if not part.is_multipart())
match = re.search(r"token(?:=|%3D)([A-Za-z0-9_.%\-]+)", body)
assert match, "Verification link was missing from the local email"
verified = post("/api/auth/verify-email/", {"token": unquote(match[1])})
assert verified.get("email_verified"), verified
login = post("/api/auth/signin/password/", {"email": email, "password": password})
assert login.get("access_token"), "Verified account could not sign in"
print("PASS: frontend signup -> local MailHog email -> token verification -> password sign-in")
