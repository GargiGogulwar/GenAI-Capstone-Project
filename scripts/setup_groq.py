"""Prepare a local capstone environment, preserving existing values and data."""
import base64
import getpass
import os
from pathlib import Path
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
path = ROOT / ".env"
lines = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
values = dict(line.split("=", 1) for line in lines if "=" in line and not line.lstrip().startswith("#"))
key = values.get("GROQ_API_KEY") or values.get("AI_GROQ_API_KEY") or getpass.getpass("Groq API key: ").strip()
if not key.startswith("gsk_"):
    raise SystemExit("A valid Groq key is required. No files changed.")
defaults = {
    "POSTGRES_USER": "kraivor", "POSTGRES_DB": "kraivor",
    "POSTGRES_PASSWORD": secrets.token_hex(24), "REDIS_PASSWORD": secrets.token_hex(24),
    "SECRET_KEY": secrets.token_urlsafe(48), "INTERNAL_REQUEST_TOKEN": secrets.token_urlsafe(32),
    "AI_KEY_ENCRYPTION_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
    "OAUTH_ENCRYPTION_KEY_PATH": ".keys/oauth-encryption.key",
    "JWT_PRIVATE_KEY_PATH": ".keys/jwt-private.pem", "JWT_PUBLIC_KEY_PATH": ".keys/jwt-public.pem",
    "JWT_ALGORITHM": "RS256", "APP_ENV": "development", "DEBUG": "False",
    "ALLOWED_HOSTS": "localhost,127.0.0.1,identity,core,ai,frontend",
    "FRONTEND_URL": "http://localhost:3000", "COOKIE_PATH": "/api/auth/",
    "COOKIE_SECURE": "false", "COOKIE_SAMESITE": "Lax", "COOKIE_DOMAIN": "",
    "CORS_ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:8088",
    "AI_GROQ_MODEL": "openai/gpt-oss-120b", "AI_GROQ_FAST_MODEL": "openai/gpt-oss-20b",
    "AI_EMBEDDING_PROVIDER": "local", "AI_API_URL": "http://ai:8004",
    "DYNAMODB_CHAT_TABLE": "kraivor-chat-messages", "AWS_REGION": "us-east-1",
    "AWS_ACCESS_KEY_ID": "local", "AWS_SECRET_ACCESS_KEY": "local",
    "ANALYSIS_S3__ACCESS_KEY_ID": "local", "ANALYSIS_S3__SECRET_ACCESS_KEY": "local",
    "ANALYSIS_S3__ENDPOINT_URL": "http://minio:9000", "ANALYSIS_S3__USE_SSL": "false",
}
for name, value in defaults.items():
    if not values.get(name):
        values[name] = value
values["GROQ_API_KEY"] = key
values["AI_GROQ_API_KEY"] = key
# Retain comments and existing ordering; replace matching settings in place.
written = set()
output = []
for line in lines:
    name = line.split("=", 1)[0]
    if name in values and not line.lstrip().startswith("#"):
        if name not in written:
            output.append(f"{name}={values[name]}")
            written.add(name)
    else:
        output.append(line)
output += [f"{k}={v}" for k, v in values.items() if k not in written]
path.write_text("\n".join(output) + "\n", encoding="utf-8")
(ROOT / ".keys").mkdir(exist_ok=True)
compose = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.groq.yml"]
subprocess.run(compose + ["build"], check=True)
key_script = """
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.fernet import Fernet
root=Path('/app/.keys');root.mkdir(exist_ok=True)
private=root/'jwt-private.pem';public=root/'jwt-public.pem'
if not private.exists():
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    private.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
if not public.exists():
    key=serialization.load_pem_private_key(private.read_bytes(),password=None)
    public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
oauth=root/'oauth-encryption.key'
if not oauth.exists(): oauth.write_bytes(Fernet.generate_key())
"""
subprocess.run(compose + ["run", "--rm", "--no-deps", "--user", "root", "--entrypoint", "python", "identity", "-c", key_script], check=True)
subprocess.run(compose + ["up", "-d", "--wait", "--wait-timeout", "240"], check=True)
print("Kraivor Groq capstone: http://localhost:3000 | local verification emails: http://localhost:8025")
