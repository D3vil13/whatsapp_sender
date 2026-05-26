def daily_cap_for_warmup_day(warmup_day: int) -> int:
    if warmup_day <= 7:
        return 50
    if warmup_day <= 14:
        return 100
    return 200
