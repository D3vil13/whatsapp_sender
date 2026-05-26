"""Factory for Django settings shared across BulkPing microservices."""

from __future__ import annotations

import os
from pathlib import Path

from bulkping_common.config import load_service_config


def build_settings(
    *,
    service_name: str,
    installed_apps: list[str],
    root_urlconf: str,
    wsgi_application: str,
    extra_middleware: list[str] | None = None,
) -> dict:
    cfg = load_service_config()
    base_dir = Path(__file__).resolve().parent.parent

    middleware = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
    if extra_middleware:
        middleware = extra_middleware + middleware

    return {
        "SERVICE_NAME": service_name,
        "BULKPING_CONFIG": cfg,
        "BASE_DIR": base_dir,
        "SECRET_KEY": cfg.secret_key,
        "DEBUG": cfg.debug,
        "ALLOWED_HOSTS": cfg.allowed_hosts,
        "ROOT_URLCONF": root_urlconf,
        "WSGI_APPLICATION": wsgi_application,
        "INSTALLED_APPS": [
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "rest_framework",
            "corsheaders",
            *installed_apps,
        ],
        "MIDDLEWARE": middleware,
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get("POSTGRES_DB", "bulkping"),
                "USER": os.environ.get("POSTGRES_USER", "bulkping"),
                "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "bulkping"),
                "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
                "PORT": os.environ.get("POSTGRES_PORT", "5432"),
                "OPTIONS": {
                    "options": f"-c search_path={os.environ.get('DATABASE_SCHEMA', 'public')}"
                },
            }
        },
        "LANGUAGE_CODE": "en-us",
        "TIME_ZONE": cfg.celery_timezone,
        "USE_I18N": True,
        "USE_TZ": True,
        "STATIC_URL": "static/",
        "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
        "REST_FRAMEWORK": {
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "core.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_RENDERER_CLASSES": [
                "rest_framework.renderers.JSONRenderer",
            ],
            "UNAUTHENTICATED_USER": None,
        },
        "CORS_ALLOW_ALL_ORIGINS": cfg.debug,
        "CACHES": {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": cfg.redis_url,
            }
        },
    }
