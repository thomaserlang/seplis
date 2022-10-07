from pydantic import BaseModel, constr
from typing import Literal
from datetime import date
from .image import Image


class Search_schema(BaseModel):
    query: list[constr(min_length=1, max_length=200)] | None
    title: list[constr(min_length=1, max_length=200)] | None
    type: list[Literal['series', 'movie']] | None


class Search_title_document(BaseModel):
    type: str
    id: int
    title: str | None
    titles: list[dict[str, str]] | None
    release_date: date | None
    imdb: str | None
    poster_image: Image | None

    class Config:
        orm_mode = True