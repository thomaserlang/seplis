from typing import Literal

from pydantic import BaseModel, ConfigDict

from .movie import Movie
from .series import Series


class User_watched(BaseModel):
    type: Literal['movie', 'series']
    data: Movie | Series
    movie: Movie | None = None
    series: Series | None = None

    model_config = ConfigDict(from_attributes=True)
