from dataclasses import dataclass
from typing import NotRequired, TypedDict

from .user_field_constraints_schemas import ConstrainedLang


@dataclass(slots=True, kw_only=True)
class SubtitleLanguage:
    subtitle_lang: ConstrainedLang | None = None
    audio_lang: ConstrainedLang | None = None


class UserSeriesSettingsUpdate(TypedDict, total=False):
    subtitle_lang: NotRequired[ConstrainedLang | None]
    audio_lang: NotRequired[ConstrainedLang | None]


@dataclass(slots=True, kw_only=True)
class UserSeriesSettings:
    subtitle_lang: str | None = None
    audio_lang: str | None = None


@dataclass(slots=True, kw_only=True)
class UserSeriesStats:
    series_watchlist: int
    series_watched: int
    series_finished: int
    episodes_watched: int
    episodes_watched_minutes: int
