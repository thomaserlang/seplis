from pydantic import BaseModel
from datetime import date
from .image import Image


class Search_title_document_title(BaseModel):
    title: str

class Search_title_document(BaseModel, orm_mode=True):
    type: str
    id: int
    title: str | None
    titles: list[Search_title_document_title] | None
    release_date: date | None
    imdb: str | None
    poster_image: Image | None
    popularity: float | None