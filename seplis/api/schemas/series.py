from typing import Literal
from pydantic import BaseModel, ConfigDict, constr, conint, confloat, field_validator, validator, Field
from datetime import datetime, date
from .image import Image
from .genre import Genre
from .episode import Episode_create, Episode_update, Episode, User_can_watch


class Series_importers(BaseModel):
    info: constr(min_length=1, max_length=45, strip_whitespace=True) | None = None
    episodes: constr(min_length=1, max_length=45, strip_whitespace=True) | None = None


class Series_user_rating_update(BaseModel):
    rating: conint(ge=1, le=10)

class Series_user_rating(BaseModel):
    rating: int | None = None
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class Series_create(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None = None
    original_title: constr(min_length=1, max_length=200, strip_whitespace=True) | None = None
    alternative_titles: list[constr(min_length=1, max_length=200, strip_whitespace=True)] | None = None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True, to_lower=True), constr(min_length=0, max_length=45, strip_whitespace=True) | None] | None = {}
    status: conint(gt=-1) | None = None
    plot: constr(min_length=1, max_length=2000, strip_whitespace=True) | None = None
    tagline: constr(min_length=1, max_length=500, strip_whitespace=True) | None = None
    premiered: date | None = None
    ended: date | None = None
    importers: Series_importers | None = None
    runtime: conint(gt=0, lt=2880) | None = None
    genre_names: list[constr(max_length=100) | int] | None = None
    episode_type: conint(gt=0, lt=4) | None = None
    language: constr(min_length=1, max_length=100, strip_whitespace=True) | None = None
    poster_image_id: conint(gt=0) | None = None
    popularity: confloat(ge=0.0) | None = None
    rating: confloat(ge=0.0, le=10.0) | None = None
    rating_votes: conint(ge=0) | None = None
    episodes: list[Episode_create] | None = None
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid',
    )

    @field_validator('externals')
    @classmethod
    def externals_none_value(cls, v):
        for e in v:
            if v[e] == '':
                v[e] = None
        return v


class Series_update(Series_create):
    episodes: list[Episode_update] | None = None


class Series_watchlist(BaseModel):
    on_watchlist: bool = False
    created_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class Series_favorite(BaseModel):
    favorite: bool = False
    created_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class Series_season(BaseModel):
    season: int
    from_: int = Field(..., alias='from')
    to: int
    total: int
    
    model_config = ConfigDict(populate_by_name=True)


class Series(BaseModel):
    id: int
    title: str | None = None
    original_title: str | None = None
    alternative_titles: list[str]
    externals: dict[str, str]
    plot: str | None = None
    tagline: str | None = None
    premiered: date | None = None
    ended: date | None = None
    importers: Series_importers = Series_importers()
    runtime: int | None = None
    genres: list[Genre] = []
    episode_type: int | None = None
    language: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    status: int
    seasons: list[Series_season] = []
    total_episodes: int = 0
    poster_image: Image | None = None
    popularity: float | None = None
    rating: float | None = None
    rating_votes: int | None = None
    user_watchlist: Series_watchlist | None = None
    user_favorite: Series_favorite | None = None
    user_last_episode_watched: Episode | None = None
    user_rating: Series_user_rating | None = None
    user_can_watch: User_can_watch | None = None
    
    model_config = ConfigDict(from_attributes=True)

    def to_request(self):
        data = Series_update.model_validate(self)
        data.poster_image_id = self.poster_image.id if self.poster_image else None
        data.genre_names = [g.name for g in self.genres]

class Series_user_stats(BaseModel):
    episodes_watched: int = 0
    episodes_watched_minutes: int = 0
    
    model_config = ConfigDict(from_attributes=True)


SERIES_USER_SORT_TYPE = Literal[
    'user_watchlist_added_at_asc', 
    'user_watchlist_added_at_desc', 
    'user_favorite_added_at_asc', 
    'user_favorite_added_at_desc', 
    'user_rating_asc', 
    'user_rating_desc',
    'user_last_episode_watched_at_asc',
    'user_last_episode_watched_at_desc',
    'rating_asc',
    'rating_desc',
    'popularity_asc',
    'popularity_desc',
    'user_play_server_series_added_asc',
    'user_play_server_series_added_desc',
    'premiered_asc',
    'premiered_desc',
]


SERIES_EXPAND = Literal[
    'user_watchlist',
    'user_favorite',
    'user_can_watch',
    'user_last_episode_watched',
    'user_rating',
]


class Series_with_episodes(Series):
    episodes: list[Episode] = []


class Series_and_episode(BaseModel):
    series: Series
    episode: Episode
    
    model_config = ConfigDict(from_attributes=True)


class Series_air_dates(BaseModel):
    air_date: date
    series: list[Series_with_episodes]
    
    model_config = ConfigDict(from_attributes=True)