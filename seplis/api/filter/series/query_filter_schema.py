from typing import Annotated
from pydantic.dataclasses import dataclass
from fastapi import Depends, Query
from datetime import date
from ...dependencies import get_current_user_no_raise
from ... import schemas


@dataclass
class Series_query_filter:
    genre_id: Annotated[list[int] | None, Query()] = None
    not_genre_id: Annotated[list[int] | None, Query()] = None
    user_can_watch: Annotated[bool | None, Query()] = None
    user_watchlist: Annotated[bool | None, Query()] = None
    user_favorites: Annotated[bool | None, Query()] = None
    user_has_watched: Annotated[bool | None, Query()] = None
    sort: Annotated[list[schemas.SERIES_USER_SORT_TYPE], Query()] = Query(default=['popularity_desc'])
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise)
    expand: Annotated[list[schemas.SERIES_EXPAND] | None, Query()] = None
    premiered_gt: Annotated[date | None, Query()] = None
    premiered_lt: Annotated[date | None, Query()] = None