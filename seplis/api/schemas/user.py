from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

type ConstrainedLang = Annotated[str, Field(min_length=1, max_length=20)]
type UsernameStr = Annotated[
    str,
    StringConstraints(
        min_length=2, max_length=45, pattern='^[A-Za-z0-9-_]+$', strip_whitespace=True
    ),
]
type PasswordStr = Annotated[str, Field(min_length=10)]


class Subtitle_language(BaseModel):
    subtitle_lang: ConstrainedLang | None = None
    audio_lang: ConstrainedLang | None = None


class User_authenticated(BaseModel):
    id: int
    token: str | None = None
    scopes: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class User_create(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: PasswordStr


class User_update(BaseModel):
    email: EmailStr | None
    username: UsernameStr | None


class User_basic(BaseModel):
    id: int
    username: str
    created_at: datetime
    scopes: list[str]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def scopes_check_str(self) -> User_basic:
        if isinstance(self.scopes, str):
            self.scopes = self.scopes.split(' ')
        return self


class User(User_basic):
    email: str


class User_public(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class User_change_password(BaseModel):
    current_password: Annotated[str, Field(min_length=1)]
    new_password: PasswordStr


class Token_create(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class User_series_settings_update(BaseModel):
    subtitle_lang: ConstrainedLang | None = None
    audio_lang: ConstrainedLang | None = None


class User_series_settings(BaseModel):
    subtitle_lang: str | None = None
    audio_lang: str | None = None

    model_config = ConfigDict(from_attributes=True)


class User_series_stats(BaseModel):
    series_watchlist: int
    series_watched: int
    series_finished: int
    episodes_watched: int
    episodes_watched_minutes: int

    model_config = ConfigDict(from_attributes=True)
