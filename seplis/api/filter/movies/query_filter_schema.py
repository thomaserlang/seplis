from datetime import date
from typing import Annotated

from fastapi import Depends, Query
from pydantic import Field
from pydantic.dataclasses import dataclass

from ... import schemas
from ...dependencies import get_current_user_no_raise


@dataclass
class Movie_query_filter:
    sort: Annotated[
        list[schemas.MOVIE_USER_SORT_TYPE],
        Query(default_factory=lambda: ['rating_desc']),
    ]
    genre_id: Annotated[list[int] | None, Query()] = None
    not_genre_id: Annotated[list[int] | None, Query()] = None
    collection_id: Annotated[list[int] | None, Query()] = None
    user_can_watch: Annotated[bool | None, Query()] = None
    user_watchlist: Annotated[bool | None, Query()] = None
    user_favorites: Annotated[bool | None, Query()] = None
    user_has_watched: Annotated[bool | None, Query()] = None
    user: Annotated[
        schemas.User_authenticated | None, Depends(get_current_user_no_raise)
    ] = None
    expand: Annotated[list[schemas.MOVIE_EXPAND] | None, Query()] = None
    release_date_gt: Annotated[date | None, Query()] = None
    release_date_lt: Annotated[date | None, Query()] = None
    rating_gt: Annotated[int | None, Query(), Field(ge=0, le=10)] = None
    rating_lt: Annotated[int | None, Query(), Field(ge=0, le=10)] = None
    rating_votes_gt: Annotated[int | None, Query(), Field(ge=0)] = None
    rating_votes_lt: Annotated[int | None, Query(), Field(ge=0)] = None
    language: Annotated[list[str] | None, Query()] = None
