from typing_extensions import Annotated
from pydantic import conint
from pydantic.dataclasses import dataclass
from fastapi import Depends, Query
from datetime import date
from ...dependencies import get_current_user_no_raise
from ... import schemas


@dataclass
class Movie_query_filter:
    genre_id: Annotated[list[int] | None, Query()] = None
    not_genre_id: Annotated[list[int] | None, Query()] = None
    collection_id: Annotated[list[int] | None, Query()] = None
    user_can_watch: Annotated[bool | None, Query()] = None
    user_watchlist: Annotated[bool | None, Query()] = None
    user_favorites: Annotated[bool | None, Query()] = None
    user_has_watched: Annotated[bool | None, Query()] = None
    sort: Annotated[list[schemas.MOVIE_USER_SORT_TYPE], Query()] = Query(default=['rating_desc'])
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise)
    expand: Annotated[list[schemas.MOVIE_EXPAND] | None, Query()] = None
    release_date_gt: Annotated[date | None, Query()] = None
    release_date_lt: Annotated[date | None, Query()] = None
    rating_gt: Annotated[conint(ge=0, le=10) | None, Query()] = None
    rating_lt: Annotated[conint(ge=0, le=10) | None, Query()] = None
    rating_votes_gt: Annotated[conint(ge=0) | None, Query()] = None
    rating_votes_lt: Annotated[conint(ge=0) | None, Query()] = None