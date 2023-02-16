from pydantic import BaseModel, AnyHttpUrl, conint
from pydantic.generics import GenericModel
from typing import TypeVar, Generic


T = TypeVar('T')


class Page_cursor_query(BaseModel):
    cursor: str | None
    per_page: conint(ge=1, le=100) = 25


class Page_cursor_result(GenericModel, Generic[T]):
    items: list[T]
    cursor: str | None = None


class Page_cursor_total_result(Page_cursor_result, Generic[T]):
    total: int = 0