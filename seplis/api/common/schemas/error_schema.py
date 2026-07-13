from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, kw_only=True)
class Error:
    code: int
    message: str
    extra: Any
    errors: list[Any] | None = None
