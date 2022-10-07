from pydantic import BaseModel, AnyHttpUrl, conint
from pydantic.generics import GenericModel
from typing import TypeVar, Generic


T = TypeVar('T')

class Page_cursor_query(BaseModel):
    before: str | None
    after: str | None
    limit = 25


class Page_cursor_links(BaseModel):
    next: AnyHttpUrl | None
    prev: AnyHttpUrl | None


class Page_cursor_result(GenericModel, Generic[T]):
    items: list[T]
    links = Page_cursor_links()


class Page_query(BaseModel):
    page: conint(ge=1) = 1
    per_page: conint(ge=1, le=100) = 25


class Page_links(BaseModel):
    next: AnyHttpUrl | None
    prev: AnyHttpUrl | None
    first: AnyHttpUrl | None
    last: AnyHttpUrl | None


class Page_result(GenericModel, Generic[T]):
    items: list[T]
    links = Page_links()
    total: int
    per_page: int
    page: int
    pages: int