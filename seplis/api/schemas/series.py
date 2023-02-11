from typing import Literal
from pydantic import BaseModel, constr, conint, confloat, validator, Field
from datetime import datetime, date
from .image import Image
from .genre import Genre
from .episode import Episode_create, Episode_update, Episode, Episode_watched


class Series_importers(BaseModel):
    info: constr(min_length=1, max_length=45, strip_whitespace=True) | None
    episodes: constr(min_length=1, max_length=45, strip_whitespace=True) | None


class Series_user_rating_update(BaseModel):
    rating: conint(ge=1, le=10)

class Series_user_rating(BaseModel):
    rating: int | None

    class Config:
        orm_mode = True


class Series_create(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    original_title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: list[constr(min_length=1, max_length=100, strip_whitespace=True)] | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True, to_lower=True), constr(min_length=0, max_length=45, strip_whitespace=True) | None] | None = {}
    status: conint(gt=-1) | None
    plot: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    tagline: constr(min_length=1, max_length=500, strip_whitespace=True) | None
    premiered: date | None
    ended: date | None
    importers: Series_importers | None
    runtime: conint(gt=0, lt=1440) | None
    genres: list[str | int] | None
    episode_type: conint(gt=0, lt=4) | None
    language: constr(min_length=1, max_length=100, strip_whitespace=True) | None
    poster_image_id: conint(gt=0) | None
    popularity: confloat(ge=0.0) | None
    rating: confloat(ge=0.0, le=10.0) | None
    episodes: list[Episode_create] | None
    
    class Config:
        extra = 'forbid'
        validate_assignment = True

    @validator('externals')
    def externals_none_value(cls, externals):
        for e in externals:
            if externals[e] == '':
                externals[e] = None
        return externals


class Series_update(Series_create):
    episodes: list[Episode_update] | None


class Series_season(BaseModel, allow_population_by_field_name=True):
    season: int
    from_: int = Field(..., alias='from')
    to: int
    total: int

class Series(BaseModel):
    id: int
    title: str | None
    original_title: str | None
    alternative_titles: list[str]
    externals: dict[str, str]
    plot: str | None
    tagline: str | None
    premiered: date | None
    ended: date | None
    importers = Series_importers()
    runtime: int | None
    genres: list[Genre] = []
    episode_type: int | None
    language: str | None
    created_at: datetime
    updated_at: datetime | None
    status: int
    seasons: list[Series_season] = []
    total_episodes: int = 0
    poster_image: Image | None
    popularity: float | None
    rating: float | None
    
    class Config:
        orm_mode = True

class Series_user_stats(BaseModel):
    episodes_watched: int = 0
    episodes_watched_minutes: int = 0

    class Config:
        orm_mode = True


class Series_following(BaseModel):
    following: bool = False
    created_at: datetime | None = None

    class Config:
        orm_mode = True


SERIES_USER_SORT_TYPE = Literal[
    'followed_at_asc', 
    'followed_at_desc', 
    'user_rating_asc', 
    'user_rating_desc',
    'watched_at_asc',
    'watched_at_desc',
]

class Series_user(BaseModel):
    series: Series
    rating: int | None
    following: bool
    last_episode_watched: Episode | None 
    last_episode_watched_data: Episode_watched | None

    class Config:
        orm_mode = True


class Series_with_episodes(Series):
    episodes: list[Episode] = []


class Series_and_episode(BaseModel):
    series: Series
    episode: Episode

    class Config:
        orm_mode = True


class Series_air_dates(BaseModel):
    air_date: date
    series: list[Series_with_episodes]

    class Config:
        orm_mode = True