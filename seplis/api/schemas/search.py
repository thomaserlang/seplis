from pydantic import BaseModel, ConfigDict
from datetime import date
from .image import Image
from .genre import Genre


class Search_title_document_title(BaseModel):
    title: str

class Search_title_document(BaseModel):
    type: str
    id: int
    title: str | None = None
    titles: list[Search_title_document_title] | None = None
    release_date: date | None = None
    imdb: str | None = None
    rating: float | None = None
    rating_votes: int | None = None
    poster_image: Image | None = None
    popularity: float | None = None
    genres: list[Genre] | None = None
    seasons: int | None = None
    episodes: int | None = None
    runtime: int | None = None
    language: str | None = None
    
    model_config = ConfigDict(from_attributes=True)