from pydantic import BaseModel, AnyHttpUrl, constr, conint
from datetime import datetime, date, time
from .image import Image

class Description_schema(BaseModel):
    text: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    title: constr(min_length=1, max_length=45, strip_whitespace=True) | None
    url: AnyHttpUrl | None


class Episode_create(BaseModel):
    title: constr(max_length=200, strip_whitespace=True) | None
    number: conint(gt=0)
    season: conint(gt=0) | None
    episode: conint(gt=0) | None
    air_date: date | None
    air_time: time | None
    air_datetime: datetime | None
    description: Description_schema | None
    runtime: conint(ge=0) | None


class Episode_update(Episode_create):
    pass


class Episode(Episode_create):
    pass

    class Config:
        orm_mode = True


class Series_importers(BaseModel):
    info: constr(min_length=1, max_length=45, strip_whitespace=True) | None
    episodes: constr(min_length=1, max_length=45, strip_whitespace=True) | None


class Series_base(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: list[constr(min_length=1, max_length=100, strip_whitespace=True)] | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True), constr(min_length=1, max_length=45, strip_whitespace=True) | None] | None
    status: conint(gt=-1) | None
    description: Description_schema | None
    premiered: date | None
    ended: date | None
    importers: Series_importers | None
    runtime: conint(gt=0, lt=1440) | None
    genres: list[constr(min_length=1, max_length=45)] | None
    episode_type: conint(gt=0, lt=4) | None
    language: constr(min_length=1, max_length=100, strip_whitespace=True) | None


class Series_create(Series_base):
    poster_image_id: conint(gt=0) | None
    episodes: list[Episode] | None


class Series_update(Series_create):
    pass


class Series(Series_base):
    id: int
    created_at: datetime
    updated_at: datetime | None
    status: int
    fans: int
    seasons: list[dict[str, int]]
    total_episodes: int
    poster_image: Image | None

    class Config:
        orm_mode = True


class Series_user_stats(BaseModel):
    episodes_watched: int = 0
    episodes_watched_minutes: int = 0

    class Config:
        orm_mode = True