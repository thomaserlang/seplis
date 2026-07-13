from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Annotated, NotRequired, TypedDict

from pydantic import Field, StringConstraints

EpisodeTitle = Annotated[str, StringConstraints(max_length=200, strip_whitespace=True)]
EpisodePlot = Annotated[
    str, StringConstraints(min_length=1, max_length=2000, strip_whitespace=True)
]


class EpisodeWatchedIncrement(TypedDict, total=False):
    watched_at: datetime


@dataclass(slots=True, kw_only=True)
class EpisodeWatched:
    episode_number: int
    times: int = 0
    position: int = 0
    watched_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class UserCanWatch:
    on_play_server: bool = False


class EpisodeCreate(TypedDict):
    title: EpisodeTitle
    number: Annotated[int, Field(gt=0)]
    original_title: NotRequired[EpisodeTitle | None]
    season: NotRequired[Annotated[int, Field(gt=0)] | None]
    episode: NotRequired[Annotated[int, Field(gt=0)] | None]
    air_date: NotRequired[date | None]
    air_datetime: NotRequired[datetime | None]
    plot: NotRequired[EpisodePlot | None]
    runtime: NotRequired[Annotated[int, Field(ge=0)] | None]
    rating: NotRequired[Annotated[float, Field(ge=0.0, le=10.0)] | None]


class EpisodeUpdate(TypedDict, total=False):
    title: NotRequired[EpisodeTitle | None]
    original_title: NotRequired[EpisodeTitle | None]
    number: NotRequired[Annotated[int, Field(gt=0)]]
    season: NotRequired[Annotated[int, Field(gt=0)] | None]
    episode: NotRequired[Annotated[int, Field(gt=0)] | None]
    air_date: NotRequired[date | None]
    air_datetime: NotRequired[datetime | None]
    plot: NotRequired[EpisodePlot | None]
    runtime: NotRequired[Annotated[int, Field(ge=0)] | None]
    rating: NotRequired[Annotated[float, Field(ge=0.0, le=10.0)] | None]


@dataclass(slots=True, kw_only=True)
class Episode:
    number: int
    title: str | None = None
    original_title: str | None = None
    season: int | None = None
    episode: int | None = None
    air_date: date | None = None
    air_datetime: datetime | None = None
    plot: str | None = None
    runtime: int | None = None
    rating: float | None = None
    user_watched: EpisodeWatched | None = None
    user_can_watch: UserCanWatch | None = None
