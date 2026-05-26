from __future__ import annotations

import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings

from bulkping_common.http import ServiceClient

IST = ZoneInfo("Asia/Kolkata")


def contacts_client() -> ServiceClient:
    cfg = settings.BULKPING_CONFIG
    return ServiceClient(cfg.contacts_service_url, cfg.internal_service_token)


def fetch_group_contacts(user_id: uuid.UUID, group_id: uuid.UUID) -> list[dict]:
    client = contacts_client()
    data = client.get(f"/internal/groups/{group_id}/contacts/", user_id=user_id)
    return data.get("contacts", [])


def broadcast_hours_warning(scheduled_at: datetime | None) -> str | None:
    if scheduled_at is None:
        return None
    local = scheduled_at.astimezone(IST)
    if local.hour < 8 or local.hour >= 21:
        return (
            "Scheduled time is outside recommended broadcast hours (08:00–21:00 IST). "
            "Sending outside these hours may increase ban risk."
        )
    return None
