from dataclasses import dataclass
from typing import Literal

from seplis.api.movie import Movie
from seplis.api.series import Series


@dataclass(slots=True, kw_only=True)
class UserWatched:
    type: Literal['movie', 'series']
    data: Movie | Series
    movie: Movie | None = None
    series: Series | None = None
