from pydantic.dataclasses import dataclass
from fastapi import Depends, Query
from ...dependencies import get_current_user_no_raise
from ... import schemas


@dataclass
class Movie_query_filter:
    genre_id: list[int] = Query(default=[])
    user_can_watch: bool = Query(default=None)
    user_stared: bool = Query(default=None)
    user_has_watched: bool = Query(default=None)
    sort: list[schemas.MOVIE_USER_SORT_TYPE] = Query(default=['popularity_desc'])
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise)
    expand: list[schemas.MOVIE_EXPAND] = Query(default=[])