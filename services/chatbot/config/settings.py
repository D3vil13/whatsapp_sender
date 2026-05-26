import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_base"))
from django_settings import build_settings
_settings = build_settings(
    service_name="chatbot",
    installed_apps=["chatbot_app"],
    root_urlconf="config.urls",
    wsgi_application="config.wsgi.application",
)
globals().update(_settings)
