from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, constr, conint
from datetime import datetime, timedelta
from .user import User_public
from .helper import default_datetime

class Play_server_create(BaseModel):
    name: constr(min_length=1, max_length=45)
    url: constr(min_length=1, max_length=200)
    secret: constr(min_length=20, max_length=200)    


class Play_server_update(BaseModel):
    name: constr(min_length=1, max_length=45) | None = None
    url: constr(min_length=1, max_length=200) | None = None
    secret: constr(min_length=20, max_length=200) | None = None


class Play_server(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class Play_server_with_url(Play_server):
    url: str

class Play_server_with_secret(Play_server_with_url):
    secret: str


class Play_request(BaseModel):
    play_id: str
    play_url: str


class Play_id_info_base(BaseModel):
    exp: Annotated[datetime, Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=8))]

class Play_id_info_episode(Play_id_info_base):
    type: str = 'series'
    series_id: int
    number: int

class Play_id_info_movie(Play_id_info_base):
    type: str = 'movie'
    movie_id: int


class Play_server_invite_create(BaseModel):
    user_id: int


class Play_server_invite_id(BaseModel):
    invite_id: str

    model_config = ConfigDict(from_attributes=True)


class Play_server_invite(BaseModel):
    user: User_public
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Play_server_access(BaseModel):
    user: User_public
    created_at: datetime


class Play_server_movie_create(BaseModel):
    movie_id: int
    created_at: datetime = default_datetime


class Play_server_episode_create(BaseModel):
    series_id: int
    episode_number: conint(ge=1)
    created_at: datetime = default_datetime