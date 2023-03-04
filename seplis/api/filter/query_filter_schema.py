from dataclasses import dataclass
from fastapi import Depends, Query
from ..schemas.user import User_authenticated
from ..dependencies import get_current_user_no_raise, get_expand
from .. import schemas


@dataclass
class Series_query_filter:
    genre_id: list[int] = Query(default=[])
    user_can_watch: bool = Query(default=None)
    user_following: bool = Query(default=None)
    user_has_watched: bool = Query(default=None)
    sort: schemas.SERIES_USER_SORT_TYPE = 'popularity_desc'
    user: User_authenticated | None = Depends(get_current_user_no_raise)
    expand: list[schemas.SERIES_EXPAND] | None = Depends(get_expand)