from pydantic import Field
from datetime import datetime, timezone

def get_utc_datetime() -> datetime:
    return datetime.now(tz=timezone.utc)

default_datetime = Field(
    default_factory=get_utc_datetime
)