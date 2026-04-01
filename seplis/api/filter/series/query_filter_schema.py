from datetime import date
from typing import Annotated

from fastapi import Depends, Query
from pydantic import Field
from pydantic.dataclasses import dataclass

from ... import schemas
from ...dependencies import get_current_user_no_raise


@dataclass
class Series_query_filter:
    sort: Annotated[
        list[schemas.SERIES_USER_SORT_TYPE],
        Query(default_factory=lambda: ['popularity_desc']),
    ]
    user: Annotated[
        schemas.User_authenticated | None, Depends(get_current_user_no_raise)
    ] = None
    genre_id: Annotated[list[int] | None, Query()] = None
    not_genre_id: Annotated[list[int] | None, Query()] = None
    user_can_watch: Annotated[bool | None, Query()] = None
    user_watchlist: Annotated[bool | None, Query()] = None
    user_favorites: Annotated[bool | None, Query()] = None
    user_has_watched: Annotated[bool | None, Query()] = None
    expand: Annotated[list[schemas.SERIES_EXPAND] | None, Query()] = None
    premiered_gt: Annotated[date | None, Query()] = None
    premiered_lt: Annotated[date | None, Query()] = None
    rating_gt: Annotated[int | None, Query(), Field(ge=0, le=10)] = None
    rating_lt: Annotated[int | None, Query(), Field(ge=0, le=10)] = None
    rating_votes_gt: Annotated[int | None, Query(), Field(ge=0)] = None
    rating_votes_lt: Annotated[int | None, Query(), Field(ge=0)] = None
    language: Annotated[list[str] | None, Query()] = None
