from dataclasses import dataclass, field
from typing import Annotated, Any

from fastapi import Depends
from pydantic import Field


@dataclass(slots=True)
class PageCursorQuery:
    cursor: str | None = None
    per_page: Annotated[int, Field(ge=1, le=100)] = 25


PageCursorQueryDep = Annotated[PageCursorQuery, Depends()]


@dataclass(slots=True)
class PageCursor[T]:
    records: list[T]
    lookup_data: dict[str, dict[str, Any]] = field(
        default_factory=dict[str, dict[str, Any]]
    )
    cursor: str | None = None
    total: int | None = None
