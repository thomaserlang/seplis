from typing import Literal
from pydantic import BaseModel, constr, conint, confloat
from datetime import datetime, date
from .image import Image
from .helper import default_datetime


class Movie_create(BaseModel):   
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    original_title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: list[constr(min_length=1, max_length=100, strip_whitespace=True)] | None
    status: conint(gt=-1, lt=5) | None
    plot: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    tagline: constr(min_length=1, max_length=500, strip_whitespace=True) | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True), constr(min_length=1, max_length=45, strip_whitespace=True) | None] | None
    status: conint(ge=0, le=5) | None # Status: 0: Unknown, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production, 6: Canceled,
    language: constr(min_length=1, max_length=20) | None
    runtime: conint(ge=0) | None
    release_date: date | None
    poster_image_id: conint(ge=1) | None
    budget: conint(ge=0) | None
    revenue: conint(ge=0) | None
    popularity: confloat(ge=0.0) | None
    rating: confloat(ge=0.0, le=10.0) | None

    class Config:
        extra = 'forbid'


class Movie_update(Movie_create):
    pass


class Movie(BaseModel):
    id: int
    poster_image: Image | None
    title: str | None
    original_title: str | None
    alternative_titles: list[str]
    status: int | None
    plot: str | None
    tagline: str | None
    externals: dict[str, str]
    language: str | None
    runtime: int | None
    release_date: date | None
    budget: int | None
    revenue: int | None
    popularity: float | None
    rating: float | None

    class Config:
        orm_mode = True


class Movie_watched_increment(BaseModel):
    watched_at: datetime = default_datetime

class Movie_watched(BaseModel):
    times = 0
    position = 0
    watched_at: datetime | None = None

    class Config:
        orm_mode = True


class Movie_stared(BaseModel):
    created_at: datetime | None = None
    stared = False

    class Config:
        orm_mode = True


MOVIE_USER_SORT_TYPE = Literal[
    'stared_at_asc',
    'stared_at_desc',
    'watched_at_asc',
    'watched_at_desc',
]

class Movie_user(BaseModel):
    movie: Movie
    stared: bool
    watched_data: Movie_watched
    
    class Config:
        orm_mode = True