from __future__ import annotations

import uuid

from django.conf import settings
from django.core.cache import cache

from bulkping_common.evolution import EvolutionAPIClient
from bulkping_common.warmup import daily_cap_for_warmup_day

from whatsapp.models import InstanceStatus, WAInstance


def evolution_client() -> EvolutionAPIClient:
    cfg = settings.BULKPING_CONFIG
    return EvolutionAPIClient(cfg.evolution_api_url, cfg.evolution_api_key)


def instance_name_for_user(user_id: uuid.UUID) -> str:
    return f"bulkping_{str(user_id).replace('-', '')[:8]}"


def get_or_create_instance(user_id: uuid.UUID) -> WAInstance:
    instance, _ = WAInstance.objects.get_or_create(
        user_id=user_id,
        defaults={
            "instance_name": instance_name_for_user(user_id),
            "daily_cap": daily_cap_for_warmup_day(1),
        },
    )
    return instance


def store_qr_cache(instance_name: str, qr_base64: str) -> None:
    cache.set(f"qr:{instance_name}", qr_base64, timeout=300)


def get_qr_cache(instance_name: str) -> str | None:
    return cache.get(f"qr:{instance_name}")
