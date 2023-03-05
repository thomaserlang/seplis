from typing import Literal
from pydantic import BaseModel
from .series import Series
from .movie import Movie


class User_watched(BaseModel, orm_mode=True):
    type: Literal['movie', 'series']
    data: Movie | Series
