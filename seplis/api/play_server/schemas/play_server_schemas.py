from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Annotated, NotRequired, TypedDict

from pydantic import Field, StringConstraints

from seplis.api.user import UserPublic
from seplis.utils import datetime_now

PlayServerName = Annotated[str, StringConstraints(min_length=1, max_length=45)]
PlayServerUrl = Annotated[str, StringConstraints(min_length=1, max_length=200)]
PlayServerSecret = Annotated[str, StringConstraints(min_length=20, max_length=200)]


class PlayServerCreate(TypedDict):
    name: PlayServerName
    url: PlayServerUrl
    secret: PlayServerSecret


class PlayServerUpdate(TypedDict, total=False):
    name: NotRequired[PlayServerName | None]
    url: NotRequired[PlayServerUrl | None]
    secret: NotRequired[PlayServerSecret | None]


@dataclass(slots=True, kw_only=True)
class PlayServer:
    id: str
    name: str


@dataclass(slots=True, kw_only=True)
class PlayServerWithUrl(PlayServer):
    url: str


@dataclass(slots=True, kw_only=True)
class PlayServerWithSecret(PlayServerWithUrl):
    secret: str


@dataclass(slots=True, kw_only=True)
class PlayRequest:
    play_id: str
    play_url: str


@dataclass(slots=True, kw_only=True)
class PlayIdInfoBase:
    exp: datetime = field(default_factory=lambda: datetime_now() + timedelta(hours=8))


@dataclass(slots=True, kw_only=True)
class PlayIdInfoEpisode(PlayIdInfoBase):
    series_id: int
    number: int
    type: str = 'series'


@dataclass(slots=True, kw_only=True)
class PlayIdInfoMovie(PlayIdInfoBase):
    movie_id: int
    type: str = 'movie'


class PlayServerInviteCreate(TypedDict):
    user_id: int


@dataclass(slots=True, kw_only=True)
class PlayServerInviteId:
    invite_id: str


@dataclass(slots=True, kw_only=True)
class PlayServerInvite:
    user: UserPublic
    created_at: datetime
    expires_at: datetime


@dataclass(slots=True, kw_only=True)
class PlayServerAccess:
    user: UserPublic
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class RadarrResponse:
    tmdbid: int
    id: int


@dataclass(slots=True, kw_only=True)
class SonarrResponse:
    TvdbId: int


class PlayServerMovieCreate(TypedDict):
    movie_id: int
    created_at: NotRequired[datetime]


class PlayServerEpisodeCreate(TypedDict):
    series_id: int
    episode_number: Annotated[int, Field(ge=1)]
    created_at: NotRequired[datetime]
