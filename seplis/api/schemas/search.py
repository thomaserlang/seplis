from pydantic import BaseModel
from datetime import date
from .image import Image
from .genre import Genre


class Search_title_document_title(BaseModel):
    title: str

class Search_title_document(BaseModel, orm_mode=True):
    type: str
    id: int
    title: str | None
    titles: list[Search_title_document_title] | None
    release_date: date | None
    imdb: str | None
    rating: float | None
    rating_votes: int | None
    poster_image: Image | None
    popularity: float | None
    genres: list[Genre] | None
    seasons: int | None
    episodes: int | None
    runtime: int | None
    language: str | None