from pydantic.dataclasses import dataclass
from fastapi import Depends, Query
from ...dependencies import get_current_user_no_raise
from ... import schemas


@dataclass
class Series_query_filter:
    genre_id: list[int] = Query(default=[])
    user_can_watch: bool = Query(default=None)
    user_watchlist: bool = Query(default=None)
    user_favorites: bool = Query(default=None)
    user_has_watched: bool = Query(default=None)
    sort: list[schemas.SERIES_USER_SORT_TYPE] = Query(default=['popularity_desc'])
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise)
    expand: list[schemas.SERIES_EXPAND] = Query(default=[])