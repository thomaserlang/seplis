from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Annotated, Literal, NotRequired, TypedDict

from pydantic import Field, StringConstraints

from seplis.api.genre import Genre
from seplis.api.image import Image

from .movie_collection_schemas import MovieCollection

MovieShortText = Annotated[
    str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
]
MoviePlotText = Annotated[
    str, StringConstraints(min_length=0, max_length=2000, strip_whitespace=True)
]
MovieTaglineText = Annotated[
    str, StringConstraints(min_length=0, max_length=500, strip_whitespace=True)
]
MovieExternalKey = Annotated[
    str,
    StringConstraints(min_length=1, max_length=45, strip_whitespace=True, to_lower=True),
]
MovieExternalValue = Annotated[
    str, StringConstraints(min_length=0, max_length=45, strip_whitespace=True)
]


class MovieCreate(TypedDict, total=False):
    title: NotRequired[MovieShortText | None]
    original_title: NotRequired[MovieShortText | None]
    alternative_titles: NotRequired[list[MovieShortText] | None]
    status: NotRequired[Annotated[int, Field(ge=0, le=6)] | None]
    plot: NotRequired[MoviePlotText | None]
    tagline: NotRequired[MovieTaglineText | None]
    externals: NotRequired[dict[MovieExternalKey, MovieExternalValue | None] | None]
    language: NotRequired[
        Annotated[str, StringConstraints(min_length=1, max_length=20)] | None
    ]
    runtime: NotRequired[Annotated[int, Field(ge=0)] | None]
    release_date: NotRequired[date | None]
    poster_image_id: NotRequired[Annotated[int, Field(ge=1)] | None]
    budget: NotRequired[Annotated[int, Field(ge=0)] | None]
    revenue: NotRequired[Annotated[int, Field(ge=0)] | None]
    popularity: NotRequired[Annotated[float, Field(ge=0.0)] | None]
    rating: NotRequired[Annotated[float, Field(ge=0.0, le=10.0)] | None]
    rating_votes: NotRequired[Annotated[int, Field(ge=0)] | None]
    genre_names: NotRequired[
        list[Annotated[str, StringConstraints(max_length=100)] | int] | None
    ]
    collection_name: NotRequired[
        Annotated[str, StringConstraints(max_length=200)] | int | None
    ]


class MovieUpdate(MovieCreate, total=False):
    pass


class MovieWatchedIncrement(TypedDict, total=False):
    watched_at: datetime


@dataclass(slots=True, kw_only=True)
class MovieWatched:
    times: int = 0
    position: int = 0
    watched_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class MovieWatchlist:
    created_at: datetime | None = None
    on_watchlist: bool = False


@dataclass(slots=True, kw_only=True)
class MovieFavorite:
    created_at: datetime | None = None
    favorite: bool = False


@dataclass(slots=True, kw_only=True)
class Movie:
    id: int
    poster_image: Image | None = None
    title: str | None = None
    original_title: str | None = None
    alternative_titles: list[str] = field(default_factory=list)
    status: int | None = None
    plot: str | None = None
    tagline: str | None = None
    externals: dict[str, str | None] = field(default_factory=dict)
    language: str | None = None
    runtime: int | None = None
    release_date: date | None = None
    budget: int | None = None
    revenue: int | None = None
    popularity: float | None = None
    rating: float | None = None
    rating_votes: int | None = None
    genres: list[Genre] = field(default_factory=list)
    collection: MovieCollection | None = None
    user_watched: MovieWatched | None = None
    user_watchlist: MovieWatchlist | None = None
    user_favorite: MovieFavorite | None = None

    def to_request(self) -> MovieUpdate:
        return {
            'title': self.title,
            'original_title': self.original_title,
            'alternative_titles': self.alternative_titles,
            'status': self.status,
            'plot': self.plot,
            'tagline': self.tagline,
            'externals': self.externals,
            'language': self.language,
            'runtime': self.runtime,
            'release_date': self.release_date,
            'poster_image_id': self.poster_image.id if self.poster_image else None,
            'budget': self.budget,
            'revenue': self.revenue,
            'popularity': self.popularity,
            'rating': self.rating,
            'rating_votes': self.rating_votes,
            'genre_names': [genre.name for genre in self.genres],
            'collection_name': self.collection.name if self.collection else None,
        }


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
