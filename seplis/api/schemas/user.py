from pydantic import BaseModel, constr, EmailStr
from datetime import datetime
from typing import Literal


class Subtitle_language(BaseModel):
    subtitle_lang: constr(min_length=1, max_length=20) | None
    audio_lang: constr(min_length=1, max_length=20) | None


class User_authenticated(BaseModel):
    id: int
    level: int
    token: str | None

    class Config:
        orm_mode = True


USER_PASSWORD_TYPE = constr(min_length=10)

class User_create(BaseModel):
    email: EmailStr
    username: constr(min_length=2, max_length=45, regex='^[A-Za-z0-9-_]+$', strip_whitespace=True)
    password: USER_PASSWORD_TYPE


class User_update(BaseModel):
    email: EmailStr | None
    username: constr(min_length=2, max_length=45, regex='^[A-Za-z0-9-_]+$', strip_whitespace=True) | None


class User_basic(BaseModel):
    id: int
    username: str
    created_at: datetime
    level: int

    class Config:
        orm_mode = True


class User(User_basic):
    email: str


class User_public(BaseModel):
    id: int
    username: str
    
    class Config:
        orm_mode = True


class User_change_password(BaseModel):
    current_password: constr(min_length=1)
    new_password: USER_PASSWORD_TYPE


class Token_create(BaseModel):
    grant_type: Literal['password']
    username: str
    password: str
    client_id: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class User_series_settings_update(BaseModel):
    subtitle_lang: constr(min_length=1, max_length=20) | None
    audio_lang: constr(min_length=1, max_length=20) | None

class User_series_settings(BaseModel):
    subtitle_lang: str | None
    audio_lang: str | None

    class Config:
        orm_mode = True


class User_series_stats(BaseModel):
    series_following: int
    series_watched: int
    series_finished: int
    episodes_watched: int
    episodes_watched_minutes: int

    class Config:
        orm_mode = True