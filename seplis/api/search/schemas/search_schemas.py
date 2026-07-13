from dataclasses import dataclass
from datetime import date

from seplis.api.genre import Genre
from seplis.api.image import Image


@dataclass(slots=True, kw_only=True)
class SearchTitleDocumentTitle:
    title: str


@dataclass(slots=True, kw_only=True)
class SearchTitleDocument:
    type: str
    id: int
    title: str | None = None
    titles: list[SearchTitleDocumentTitle] | None = None
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
