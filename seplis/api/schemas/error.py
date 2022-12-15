from pydantic import BaseModel
from typing import Any

class Error(BaseModel):
    code: int
    errors: list[Any] | None
    message: str
    extra: Any

    class Config:
        from_orm = True