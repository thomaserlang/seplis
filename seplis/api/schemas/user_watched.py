from typing import Literal
from pydantic import BaseModel, ConfigDict
from .series import Series
from .movie import Movie


class User_watched(BaseModel):
    type: Literal['movie', 'series']
    data: Movie | Series
    
    model_config = ConfigDict(from_attributes=True)
