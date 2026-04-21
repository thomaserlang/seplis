from pydantic import BaseModel, ConfigDict

from .user_field_constraints_schemas import ConstrainedLang


class SubtitleLanguage(BaseModel):
    subtitle_lang: ConstrainedLang | None = None
    audio_lang: ConstrainedLang | None = None


class UserSeriesSettingsUpdate(BaseModel):
    subtitle_lang: ConstrainedLang | None = None
    audio_lang: ConstrainedLang | None = None


class UserSeriesSettings(BaseModel):
    subtitle_lang: str | None = None
    audio_lang: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserSeriesStats(BaseModel):
    series_watchlist: int
    series_watched: int
    series_finished: int
    episodes_watched: int
    episodes_watched_minutes: int

    model_config = ConfigDict(from_attributes=True)
