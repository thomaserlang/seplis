from pydantic import BaseModel, ConfigDict
from typing import Any

class Error(BaseModel):
    code: int
    errors: list[Any] | None = None
    message: str
    extra: Any

    model_config = ConfigDict(from_attributes=True)