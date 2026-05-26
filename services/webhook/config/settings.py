import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_base"))
from django_settings import build_settings
_settings = build_settings(
    service_name="webhook",
    installed_apps=["webhook_app"],
    root_urlconf="config.urls",
    wsgi_application="config.wsgi.application",
)
_settings["REST_FRAMEWORK"]["DEFAULT_AUTHENTICATION_CLASSES"] = []
_settings["REST_FRAMEWORK"]["DEFAULT_PERMISSION_CLASSES"] = []
globals().update(_settings)
