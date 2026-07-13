from dataclasses import dataclass
from datetime import date
from typing import Annotated

from fastapi import Depends, Query

from seplis.api.dependencies import get_current_user_no_raise
from seplis.api.series.schemas.series_schemas import (
    SERIES_EXPAND,
    SERIES_USER_SORT_TYPE,
)
from seplis.api.user import UserAuthenticated


@dataclass(slots=True)
class SeriesQueryFilter:
    sort: list[SERIES_USER_SORT_TYPE]
    user: UserAuthenticated | None = None
    genre_id: list[int] | None = None
    not_genre_id: list[int] | None = None
    user_can_watch: bool | None = None
    user_watchlist: bool | None = None
    user_favorites: bool | None = None
    user_has_watched: bool | None = None
    expand: list[SERIES_EXPAND] | None = None
    premiered_gt: date | None = None
    premiered_lt: date | None = None
    rating_gt: int | None = None
    rating_lt: int | None = None
    rating_votes_gt: int | None = None
    rating_votes_lt: int | None = None
    language: list[str] | None = None


def series_query_filter(
    sort: Annotated[
        list[SERIES_USER_SORT_TYPE],
        Query(default_factory=lambda: ['popularity_desc']),
    ],
    user: Annotated[UserAuthenticated | None, Depends(get_current_user_no_raise)] = None,
    genre_id: Annotated[list[int] | None, Query()] = None,
    not_genre_id: Annotated[list[int] | None, Query()] = None,
    user_can_watch: Annotated[bool, Query()] | None = None,
    user_watchlist: Annotated[bool, Query()] | None = None,
    user_favorites: Annotated[bool, Query()] | None = None,
    user_has_watched: Annotated[bool, Query()] | None = None,
    expand: Annotated[list[SERIES_EXPAND] | None, Query()] = None,
    premiered_gt: Annotated[date, Query()] | None = None,
    premiered_lt: Annotated[date, Query()] | None = None,
    rating_gt: Annotated[int, Query(ge=0, le=10)] | None = None,
    rating_lt: Annotated[int, Query(ge=0, le=10)] | None = None,
    rating_votes_gt: Annotated[int, Query(ge=0)] | None = None,
    rating_votes_lt: Annotated[int, Query(ge=0)] | None = None,
    language: Annotated[list[str] | None, Query()] = None,
) -> SeriesQueryFilter:
    return SeriesQueryFilter(
        sort=sort,
        user=user,
        genre_id=genre_id,
        not_genre_id=not_genre_id,
        user_can_watch=user_can_watch,
        user_watchlist=user_watchlist,
        user_favorites=user_favorites,
        user_has_watched=user_has_watched,
        expand=expand,
        premiered_gt=premiered_gt,
        premiered_lt=premiered_lt,
        rating_gt=rating_gt,
        rating_lt=rating_lt,
        rating_votes_gt=rating_votes_gt,
        rating_votes_lt=rating_votes_lt,
        language=language,
    )


SeriesQueryFilterDep = Annotated[SeriesQueryFilter, Depends(series_query_filter)]
