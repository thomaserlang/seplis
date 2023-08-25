from pydantic import BaseModel, ConfigDict, constr, conint, confloat
from datetime import datetime, date
from .helper import default_datetime


class Episode_watched_increment(BaseModel):
    watched_at: datetime = default_datetime

class Episode_watched(BaseModel):
    episode_number: int
    times: int = 0
    position: int = 0
    watched_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class User_can_watch(BaseModel):
    on_play_server: bool = False


class Episode_create(BaseModel, extra='forbid'):
    title: constr(max_length=200, strip_whitespace=True)
    original_title: constr(max_length=200, strip_whitespace=True) | None = None
    number: conint(gt=0)
    season: conint(gt=0) | None = None
    episode: conint(gt=0) | None = None
    air_date: date | None = None
    air_datetime: datetime | None = None
    plot: constr(min_length=1, max_length=2000, strip_whitespace=True) | None = None
    runtime: conint(ge=0) | None = None
    rating: confloat(ge=0.0, le=10.0) | None = None


class Episode_update(Episode_create):
    title: constr(max_length=200, strip_whitespace=True) | None = None


class Episode(BaseModel):
    title: str | None = None
    original_title: str | None = None
    number: int
    season: int | None = None
    episode: int | None = None
    air_date: date | None = None
    air_datetime: datetime | None = None
    plot: str | None = None
    runtime: int | None = None
    rating: float | None = None
    user_watched: Episode_watched | None = None
    user_can_watch: User_can_watch | None = None

    model_config = ConfigDict(from_attributes=True)