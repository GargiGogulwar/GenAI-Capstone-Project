"""Run inside identity to create an isolated, verified local demonstration user."""
import json
import os
from pathlib import Path
import secrets
import sys

sys.path.insert(0, "/app/apps")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth.settings.production")
import django
django.setup()
from users.models import User
from authentication.tokens import get_token_service

email = f"capstone-{secrets.token_hex(4)}@example.test"
password = secrets.token_urlsafe(24)
user = User.objects.create_user(email=email, password=password, name="Capstone Demo", email_verified=True)
tokens = get_token_service().generate_tokens(user)
Path("/tmp/kraivor-capstone-session.json").write_text(json.dumps({
    "email": email, "password": password, "user_id": str(user.id), "access_token": tokens.access_token,
}))
print("Created isolated demo user; credentials saved to /tmp/kraivor-capstone-session.json")
