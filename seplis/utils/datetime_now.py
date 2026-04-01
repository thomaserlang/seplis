from datetime import UTC, datetime


def datetime_now() -> datetime:
    return datetime.now(tz=UTC)
