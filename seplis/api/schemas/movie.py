from pydantic import BaseModel, constr, conint
from datetime import date
from .image import Image


class Movie_base(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: list[constr(min_length=1, max_length=100, strip_whitespace=True)] | None
    status: conint(gt=-1, lt=5) | None
    description: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True), constr(min_length=1, max_length=45, strip_whitespace=True) | None] | None
    status: conint(ge=0, le=5) | None # Status: 0: Unknown, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production, 6: Canceled,
    language: constr(min_length=1, max_length=20) | None
    runtime: conint(gt=1) | None
    release_date: date | None


class Movie_create(Movie_base):
    poster_image_id: conint(gt=1) | None


class Movie_update(Movie_create):
    pass


class Movie(Movie_create):
    id: int
    poster_image: Image | None

    class Config:
        orm_mode = True