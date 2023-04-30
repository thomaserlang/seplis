from typing import Literal
from pydantic import BaseModel, constr, conint, confloat, validator
from datetime import datetime, date
from .image import Image
from .helper import default_datetime
from .genre import Genre
from .movie_collection import Movie_collection


class Movie_create(BaseModel, extra='forbid', validate_assignment=True):   
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    original_title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: list[constr(min_length=1, max_length=200, strip_whitespace=True)] | None
    status: conint(gt=-1, lt=5) | None
    plot: constr(min_length=0, max_length=2000, strip_whitespace=True) | None
    tagline: constr(min_length=0, max_length=500, strip_whitespace=True) | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True, to_lower=True), constr(min_length=0, max_length=45, strip_whitespace=True) | None] | None
    status: conint(ge=0, le=5) | None # Status: 0: Unknown, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production, 6: Canceled,
    language: constr(min_length=1, max_length=20) | None
    runtime: conint(ge=0) | None
    release_date: date | None
    poster_image_id: conint(ge=1) | None
    budget: conint(ge=0) | None
    revenue: conint(ge=0) | None
    popularity: confloat(ge=0.0) | None
    rating: confloat(ge=0.0, le=10.0) | None
    rating_votes: conint(ge=0) | None
    genre_names: list[constr(max_length=100) | int] | None
    collection_name: constr(max_length=200) | int | None

    @validator('externals')
    def externals_none_value(cls, externals):
        for e in externals:
            if externals[e] == '':
                externals[e] = None
        return externals


class Movie_update(Movie_create, orm_mode=True):
    pass


class Movie_watched_increment(BaseModel):
    watched_at: datetime = default_datetime


class Movie_watched(BaseModel, orm_mode=True):
    times = 0
    position = 0
    watched_at: datetime | None = None


class Movie_watchlist(BaseModel, orm_mode=True):
    created_at: datetime | None = None
    on_watchlist = False


class Movie_favorite(BaseModel, orm_mode=True):
    created_at: datetime | None = None
    favorite = False


class Movie(BaseModel, orm_mode=True):
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
    rating_votes: int | None
    genres: list[Genre]
    collection: Movie_collection | None
    user_watched: Movie_watched | None
    user_watchlist: Movie_watchlist | None
    user_favorite: Movie_favorite | None

    def to_request(self):
        data = Movie_update.from_orm(self)
        data.poster_image_id = self.poster_image.id if self.poster_image else None
        data.genre_names = [g.name for g in self.genres]
        data.collection_name = self.collection.name if self.collection else None
        return data


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