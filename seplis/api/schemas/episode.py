from pydantic import BaseModel, constr, conint, confloat
from datetime import datetime, date
from .helper import default_datetime


class Episode_watched_increment(BaseModel):
    watched_at: datetime = default_datetime

class Episode_watched(BaseModel):
    episode_number: int
    times = 0
    position = 0
    watched_at: datetime | None = None

    class Config:
        orm_mode = True


class User_can_watch(BaseModel):
    on_play_server = False


class Episode_create(BaseModel):
    title: constr(max_length=200, strip_whitespace=True)
    original_title: constr(max_length=200, strip_whitespace=True) | None
    number: conint(gt=0)
    season: conint(gt=0) | None
    episode: conint(gt=0) | None
    air_date: date | None
    air_datetime: datetime | None
    plot: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    runtime: conint(ge=0) | None
    rating: confloat(ge=0.0, le=10.0) | None

    class Config:
        extra = 'forbid'


class Episode_update(Episode_create):
    title: constr(max_length=200, strip_whitespace=True) | None


class Episode(BaseModel):
    title: str | None
    original_title: str | None
    number: int
    season: int | None
    episode: int | None
    air_date: date | None
    air_datetime: datetime | None
    plot: str | None
    runtime: int | None
    rating: float | None
    user_watched: Episode_watched | None
    user_can_watch: User_can_watch | None

    class Config:
        orm_mode = True