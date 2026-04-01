from typing import Annotated, TypeVar

from pydantic import BaseModel, conint

T = TypeVar('T')


class Page_cursor_query(BaseModel):
    cursor: str | None = None
    per_page: Annotated[int, conint(ge=1, le=100)] = 25


class Page_cursor_result[T](BaseModel):
    items: list[T]
    cursor: str | None = None


class Page_cursor_total_result(Page_cursor_result[T]):
    total: int = 0
