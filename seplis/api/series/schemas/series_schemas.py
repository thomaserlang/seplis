from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Annotated, Literal, NotRequired, TypedDict

from pydantic import Field, StringConstraints

from seplis.api.genre import Genre
from seplis.api.image import Image

from .episode_schemas import Episode, EpisodeCreate, EpisodeUpdate, UserCanWatch

SeriesShortText = Annotated[
    str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
]
SeriesLongText = Annotated[
    str, StringConstraints(min_length=1, max_length=2000, strip_whitespace=True)
]
SeriesTaglineText = Annotated[
    str, StringConstraints(min_length=1, max_length=500, strip_whitespace=True)
]
SeriesExternalKey = Annotated[
    str,
    StringConstraints(min_length=1, max_length=45, strip_whitespace=True, to_lower=True),
]
SeriesExternalValue = Annotated[
    str, StringConstraints(min_length=0, max_length=45, strip_whitespace=True)
]
SeriesImporterName = Annotated[
    str, StringConstraints(min_length=1, max_length=45, strip_whitespace=True)
]


class SeriesImportersInput(TypedDict, total=False):
    info: NotRequired[SeriesImporterName | None]
    episodes: NotRequired[SeriesImporterName | None]


@dataclass(slots=True, kw_only=True)
class SeriesImporters:
    info: str | None = None
    episodes: str | None = None


class SeriesUserRatingUpdate(TypedDict):
    rating: Annotated[int, Field(ge=1, le=10)]


@dataclass(slots=True, kw_only=True)
class SeriesUserRating:
    rating: int | None = None
    updated_at: datetime | None = None


class SeriesCreate(TypedDict, total=False):
    title: NotRequired[SeriesShortText | None]
    original_title: NotRequired[SeriesShortText | None]
    alternative_titles: NotRequired[list[SeriesShortText] | None]
    externals: NotRequired[dict[SeriesExternalKey, SeriesExternalValue | None] | None]
    status: NotRequired[Annotated[int, Field(gt=-1)] | None]
    plot: NotRequired[SeriesLongText | None]
    tagline: NotRequired[SeriesTaglineText | None]
    premiered: NotRequired[date | None]
    ended: NotRequired[date | None]
    importers: NotRequired[SeriesImportersInput | SeriesImporters | None]
    runtime: NotRequired[Annotated[int, Field(gt=0, lt=2880)] | None]
    genre_names: NotRequired[
        list[Annotated[str, StringConstraints(max_length=100)] | int] | None
    ]
    episode_type: NotRequired[Annotated[int, Field(gt=0, lt=4)] | None]
    language: NotRequired[
        Annotated[
            str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
        ]
        | None
    ]
    poster_image_id: NotRequired[Annotated[int, Field(gt=0)] | None]
    popularity: NotRequired[Annotated[float, Field(ge=0.0)] | None]
    rating: NotRequired[Annotated[float, Field(ge=0.0, le=10.0)] | None]
    rating_votes: NotRequired[Annotated[int, Field(ge=0)] | None]
    episodes: NotRequired[list[EpisodeCreate] | None]


class SeriesUpdate(TypedDict, total=False):
    title: NotRequired[SeriesShortText | None]
    original_title: NotRequired[SeriesShortText | None]
    alternative_titles: NotRequired[list[SeriesShortText] | None]
    externals: NotRequired[dict[SeriesExternalKey, SeriesExternalValue | None] | None]
    status: NotRequired[Annotated[int, Field(gt=-1)] | None]
    plot: NotRequired[SeriesLongText | None]
    tagline: NotRequired[SeriesTaglineText | None]
    premiered: NotRequired[date | None]
    ended: NotRequired[date | None]
    importers: NotRequired[SeriesImportersInput | SeriesImporters | None]
    runtime: NotRequired[Annotated[int, Field(gt=0, lt=2880)] | None]
    genre_names: NotRequired[
        list[Annotated[str, StringConstraints(max_length=100)] | int] | None
    ]
    episode_type: NotRequired[Annotated[int, Field(gt=0, lt=4)] | None]
    language: NotRequired[
        Annotated[
            str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
        ]
        | None
    ]
    poster_image_id: NotRequired[Annotated[int, Field(gt=0)] | None]
    popularity: NotRequired[Annotated[float, Field(ge=0.0)] | None]
    rating: NotRequired[Annotated[float, Field(ge=0.0, le=10.0)] | None]
    rating_votes: NotRequired[Annotated[int, Field(ge=0)] | None]
    episodes: NotRequired[list[EpisodeUpdate] | None]


@dataclass(slots=True, kw_only=True)
class SeriesWatchlist:
    on_watchlist: bool = False
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class SeriesFavorite:
    favorite: bool = False
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class SeriesSeason:
    season: int
    from_: int
    to: int
    total: int


@dataclass(slots=True, kw_only=True)
class Series:
    id: int
    title: str | None = None
    original_title: str | None = None
    alternative_titles: list[str] = field(default_factory=list)
    externals: dict[str, str | None] = field(default_factory=dict)
    plot: str | None = None
    tagline: str | None = None
    premiered: date | None = None
    ended: date | None = None
    importers: SeriesImporters = field(default_factory=SeriesImporters)
    runtime: int | None = None
    genres: list[Genre] = field(default_factory=list)
    episode_type: int | None = None
    language: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    status: int | None = None
    seasons: list[SeriesSeason] = field(default_factory=list)
    total_episodes: int = 0
    poster_image: Image | None = None
    popularity: float | None = None
    rating: float | None = None
    rating_votes: int | None = None
    user_watchlist: SeriesWatchlist | None = None
    user_favorite: SeriesFavorite | None = None
    user_last_episode_watched: Episode | None = None
    user_rating: SeriesUserRating | None = None
    user_can_watch: UserCanWatch | None = None

    def to_request(self) -> SeriesUpdate:
        return {
            'title': self.title,
            'original_title': self.original_title,
            'alternative_titles': self.alternative_titles,
            'externals': self.externals,
            'status': self.status,
            'plot': self.plot,
            'tagline': self.tagline,
            'premiered': self.premiered,
            'ended': self.ended,
            'importers': self.importers,
            'runtime': self.runtime,
            'genre_names': [genre.name for genre in self.genres],
            'episode_type': self.episode_type,
            'language': self.language,
            'poster_image_id': self.poster_image.id if self.poster_image else None,
            'popularity': self.popularity,
            'rating': self.rating,
            'rating_votes': self.rating_votes,
        }


@dataclass(slots=True, kw_only=True)
class SeriesUserStats:
    episodes_watched: int = 0
    episodes_watched_minutes: int = 0


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


@dataclass(slots=True, kw_only=True)
class SeriesWithEpisodes(Series):
    episodes: list[Episode] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class SeriesAndEpisode:
    series: Series
    episode: Episode


@dataclass(slots=True, kw_only=True)
class SeriesAirDates:
    air_date: date
    series: list[SeriesWithEpisodes]
