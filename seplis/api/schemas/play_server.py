from pydantic import BaseModel, constr


class Play_server_create(BaseModel):
    name: constr(min_length=1, max_length=45)
    url: constr(min_length=1, max_length=200)
    secret: constr(min_length=20, max_length=200)    


class Play_server_update(BaseModel):
    name: constr(min_length=1, max_length=45) | None
    url: constr(min_length=1, max_length=200) | None
    secret: constr(min_length=20, max_length=200) | None


class Play_server(BaseModel):
    id: int
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
    type: str
    series_id: int
    number: int