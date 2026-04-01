from datetime import UTC, datetime

from pydantic import Field


def get_utc_datetime() -> datetime:
    return datetime.now(tz=UTC)

default_datetime = Field(
    default_factory=get_utc_datetime
)