from dataclasses import dataclass
from datetime import date
from typing import Annotated

from fastapi import Depends, Query

from seplis.api.dependencies import get_current_user_no_raise
from seplis.api.movie.schemas.movie_schemas import MOVIE_EXPAND, MOVIE_USER_SORT_TYPE
from seplis.api.user import UserAuthenticated


@dataclass(slots=True)
class MovieQueryFilter:
    sort: list[MOVIE_USER_SORT_TYPE]
    genre_id: list[int] | None = None
    not_genre_id: list[int] | None = None
    collection_id: list[int] | None = None
    user_can_watch: bool | None = None
    user_watchlist: bool | None = None
    user_favorites: bool | None = None
    user_has_watched: bool | None = None
    user: UserAuthenticated | None = None
    expand: list[MOVIE_EXPAND] | None = None
    release_date_gt: date | None = None
    release_date_lt: date | None = None
    rating_gt: int | None = None
    rating_lt: int | None = None
    rating_votes_gt: int | None = None
    rating_votes_lt: int | None = None
    language: list[str] | None = None


def movie_query_filter(
    sort: Annotated[
        list[MOVIE_USER_SORT_TYPE],
        Query(default_factory=lambda: ['rating_desc']),
    ],
    genre_id: Annotated[list[int] | None, Query()] = None,
    not_genre_id: Annotated[list[int] | None, Query()] = None,
    collection_id: Annotated[list[int] | None, Query()] = None,
    user_can_watch: Annotated[bool, Query()] | None = None,
    user_watchlist: Annotated[bool, Query()] | None = None,
    user_favorites: Annotated[bool, Query()] | None = None,
    user_has_watched: Annotated[bool, Query()] | None = None,
    user: Annotated[UserAuthenticated | None, Depends(get_current_user_no_raise)] = None,
    expand: Annotated[list[MOVIE_EXPAND] | None, Query()] = None,
    release_date_gt: Annotated[date, Query()] | None = None,
    release_date_lt: Annotated[date, Query()] | None = None,
    rating_gt: Annotated[int, Query(ge=0, le=10)] | None = None,
    rating_lt: Annotated[int, Query(ge=0, le=10)] | None = None,
    rating_votes_gt: Annotated[int, Query(ge=0)] | None = None,
    rating_votes_lt: Annotated[int, Query(ge=0)] | None = None,
    language: Annotated[list[str] | None, Query()] = None,
) -> MovieQueryFilter:
    return MovieQueryFilter(
        sort=sort,
        genre_id=genre_id,
        not_genre_id=not_genre_id,
        collection_id=collection_id,
        user_can_watch=user_can_watch,
        user_watchlist=user_watchlist,
        user_favorites=user_favorites,
        user_has_watched=user_has_watched,
        user=user,
        expand=expand,
        release_date_gt=release_date_gt,
        release_date_lt=release_date_lt,
        rating_gt=rating_gt,
        rating_lt=rating_lt,
        rating_votes_gt=rating_votes_gt,
        rating_votes_lt=rating_votes_lt,
        language=language,
    )


MovieQueryFilterDep = Annotated[MovieQueryFilter, Depends(movie_query_filter)]
