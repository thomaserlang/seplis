from pydantic import BaseModel, constr, conint
from datetime import datetime
from .user import User_public
from .helper import default_datetime

class Play_server_create(BaseModel):
    name: constr(min_length=1, max_length=45)
    url: constr(min_length=1, max_length=200)
    secret: constr(min_length=20, max_length=200)    


class Play_server_update(BaseModel):
    name: constr(min_length=1, max_length=45) | None
    url: constr(min_length=1, max_length=200) | None
    secret: constr(min_length=20, max_length=200) | None


class Play_server(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

class Play_server_with_url(Play_server):
    url: str

class Play_server_with_secret(Play_server_with_url):
    secret: str


class Play_request(BaseModel):
    play_id: str
    play_url: str


class Play_id_info_episode(BaseModel):
    type: str = 'series'
    series_id: int
    number: int

class Play_id_info_movie(BaseModel):
    type: str = 'movie'
    movie_id: int


class Play_server_invite_create(BaseModel):
    user_id: int


class Play_server_invite_id(BaseModel):
    invite_id: str

    class Config:
        orm_mode = True


class Play_server_invite(BaseModel):
    user: User_public
    created_at: datetime
    expires_at: datetime

    class Config:
        orm_mode = True


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