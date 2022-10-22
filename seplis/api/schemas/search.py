from pydantic import BaseModel
from datetime import date
from .image import Image


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