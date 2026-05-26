import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_base"))
from django_settings import build_settings
_settings = build_settings(
    service_name="campaigns",
    installed_apps=["campaigns_app"],
    root_urlconf="config.urls",
    wsgi_application="config.wsgi.application",
)
_settings["CELERY_BROKER_URL"] = _settings["BULKPING_CONFIG"].redis_url
_settings["CELERY_RESULT_BACKEND"] = _settings["BULKPING_CONFIG"].redis_url
_settings["CELERY_ACCEPT_CONTENT"] = ["json"]
_settings["CELERY_TASK_SERIALIZER"] = "json"
_settings["CELERY_RESULT_SERIALIZER"] = "json"
_settings["CELERY_TIMEZONE"] = _settings["BULKPING_CONFIG"].celery_timezone
globals().update(_settings)
