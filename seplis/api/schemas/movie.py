from typing import Literal
from pydantic import BaseModel, ConfigDict, constr, conint, confloat, field_validator
from datetime import datetime, date
from .image import Image
from .helper import default_datetime
from .genre import Genre
from .movie_collection import Movie_collection


class Movie_create(BaseModel, extra='forbid', validate_assignment=True):   
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None = None
    original_title: constr(min_length=1, max_length=200, strip_whitespace=True) | None = None
    alternative_titles: list[constr(min_length=1, max_length=200, strip_whitespace=True)] | None = None
    status: conint(gt=-1, lt=5) | None = None
    plot: constr(min_length=0, max_length=2000, strip_whitespace=True) | None = None
    tagline: constr(min_length=0, max_length=500, strip_whitespace=True) | None = None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True, to_lower=True), constr(min_length=0, max_length=45, strip_whitespace=True) | None] | None = None
    status: conint(ge=0, le=6) | None # Status: 0: Unknown, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production, 6: Canceled,
    language: constr(min_length=1, max_length=20) | None = None
    runtime: conint(ge=0) | None = None
    release_date: date | None = None
    poster_image_id: conint(ge=1) | None = None
    budget: conint(ge=0) | None = None
    revenue: conint(ge=0) | None = None
    popularity: confloat(ge=0.0) | None = None
    rating: confloat(ge=0.0, le=10.0) | None = None
    rating_votes: conint(ge=0) | None = None
    genre_names: list[constr(max_length=100) | int] | None = None
    collection_name: constr(max_length=200) | int | None = None

    @field_validator('externals')
    @classmethod
    def externals_none_value(cls, v):
        for e in v:
            if v[e] == '':
                v[e] = None
        return v


class Movie_update(Movie_create):
    pass
    
    model_config = ConfigDict(from_attributes=True)


class Movie_watched_increment(BaseModel):
    watched_at: datetime = default_datetime


class Movie_watched(BaseModel):
    times: int = 0
    position: int = 0
    watched_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class Movie_watchlist(BaseModel):
    created_at: datetime | None = None
    on_watchlist: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class Movie_favorite(BaseModel):
    created_at: datetime | None = None
    favorite: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class Movie(BaseModel):
    id: int
    poster_image: Image | None = None
    title: str | None = None
    original_title: str | None = None
    alternative_titles: list[str]
    status: int | None = None
    plot: str | None = None
    tagline: str | None = None
    externals: dict[str, str]
    language: str | None = None
    runtime: int | None = None
    release_date: date | None = None
    budget: int | None = None
    revenue: int | None = None
    popularity: float | None = None
    rating: float | None = None
    rating_votes: int | None = None
    genres: list[Genre]
    collection: Movie_collection | None = None
    user_watched: Movie_watched | None = None
    user_watchlist: Movie_watchlist | None = None
    user_favorite: Movie_favorite | None = None

    def to_request(self):
        data = Movie_update.model_validate(self)
        data.poster_image_id = self.poster_image.id if self.poster_image else None
        data.genre_names = [g.name for g in self.genres]
        data.collection_name = self.collection.name if self.collection else None
        return data
    
    model_config = ConfigDict(from_attributes=True)


MOVIE_USER_SORT_TYPE = Literal[
    'user_watchlist_added_at_asc',
    'user_watchlist_added_at_desc',
    'user_favorite_added_at_asc',
    'user_favorite_added_at_desc',
    'user_last_watched_at_asc',
    'user_last_watched_at_desc',
    'rating_asc',
    'rating_desc',
    'popularity_asc',
    'popularity_desc',
    'release_date_asc',
    'release_date_desc',
    'user_play_server_movie_added_asc',
    'user_play_server_movie_added_desc',
]


MOVIE_EXPAND = Literal[
    'user_watchlist',
    'user_favorite',
    'user_can_watch',
    'user_rating',
    'user_watched',
]