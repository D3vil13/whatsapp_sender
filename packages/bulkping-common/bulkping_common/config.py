import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceConfig:
    secret_key: str
    debug: bool
    allowed_hosts: list[str]
    database_url: str
    redis_url: str
    evolution_api_url: str
    evolution_api_key: str
    webhook_secret: str
    internal_service_token: str
    jwt_access_minutes: int
    jwt_refresh_days: int
    celery_timezone: str
    auth_service_url: str
    instance_service_url: str
    contacts_service_url: str
    campaigns_service_url: str
    chatbot_service_url: str


def _split_hosts(value: str) -> list[str]:
    return [h.strip() for h in value.split(",") if h.strip()]


def load_service_config() -> ServiceConfig:
    user = os.environ.get("POSTGRES_USER", "bulkping")
    password = os.environ.get("POSTGRES_PASSWORD", "bulkping")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "bulkping")
    schema = os.environ.get("DATABASE_SCHEMA", "public")
    database_url = os.environ.get(
        "DATABASE_URL",
        f"postgresql://{user}:{password}@{host}:{port}/{db}",
    )
    if "?" not in database_url:
        database_url = f"{database_url}?options=-c%20search_path%3D{schema}"

    return ServiceConfig(
        secret_key=os.environ["SECRET_KEY"],
        debug=os.environ.get("DEBUG", "False").lower() == "true",
        allowed_hosts=_split_hosts(os.environ.get("ALLOWED_HOSTS", "localhost")),
        database_url=database_url,
        redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        evolution_api_url=os.environ.get("EVOLUTION_API_URL", "http://localhost:8080"),
        evolution_api_key=os.environ.get("EVOLUTION_API_KEY", ""),
        webhook_secret=os.environ.get("WEBHOOK_SECRET", ""),
        internal_service_token=os.environ.get("INTERNAL_SERVICE_TOKEN", ""),
        jwt_access_minutes=int(os.environ.get("JWT_ACCESS_LIFETIME_MINUTES", "60")),
        jwt_refresh_days=int(os.environ.get("JWT_REFRESH_LIFETIME_DAYS", "7")),
        celery_timezone=os.environ.get("CELERY_TIMEZONE", "Asia/Kolkata"),
        auth_service_url=os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001"),
        instance_service_url=os.environ.get(
            "INSTANCE_SERVICE_URL", "http://localhost:8002"
        ),
        contacts_service_url=os.environ.get(
            "CONTACTS_SERVICE_URL", "http://localhost:8003"
        ),
        campaigns_service_url=os.environ.get(
            "CAMPAIGNS_SERVICE_URL", "http://localhost:8004"
        ),
        chatbot_service_url=os.environ.get(
            "CHATBOT_SERVICE_URL", "http://localhost:8005"
        ),
    )
