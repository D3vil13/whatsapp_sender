import csv
import io

import phonenumbers
from phonenumbers import NumberParseException


def normalize_phone(raw: str, default_region: str = "IN") -> str | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if not phonenumbers.is_valid_number(parsed):
            return None
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        return None


def parse_contacts_csv(file_obj) -> list[dict]:
    content = file_obj.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        name = (row.get("name") or row.get("Name") or "").strip()
        phone_raw = (row.get("phone") or row.get("Phone") or row.get("mobile") or "").strip()
        phone = normalize_phone(phone_raw)
        if name and phone:
            rows.append({"name": name, "phone": phone})
    return rows
