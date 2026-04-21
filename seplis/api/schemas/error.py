from typing import Any

from pydantic import BaseModel, ConfigDict


class Error(BaseModel):
    code: int
    errors: list[Any] | None = None
    message: str
    extra: Any

    model_config = ConfigDict(from_attributes=True)
