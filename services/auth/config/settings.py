import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_base"))

from django_settings import build_settings  # noqa: E402

_settings = build_settings(
    service_name="auth",
    installed_apps=["users"],
    root_urlconf="config.urls",
    wsgi_application="config.wsgi.application",
    extra_middleware=[],
)

# Auth service uses its own User model
_settings["AUTH_USER_MODEL"] = "users.User"
_settings["REST_FRAMEWORK"]["DEFAULT_AUTHENTICATION_CLASSES"] = []
_settings["REST_FRAMEWORK"]["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]

globals().update(_settings)
