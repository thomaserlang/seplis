from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.movie_model import MMovie
from ..models.movie_watchlist_model import MMovieWatchlist
from ..types.movie_filter_types import MovieQueryFilter


def filter_user_watchlist(query: Any, filter_query: MovieQueryFilter) -> Any:
    has_sort = (
        'user_watchlist_added_at_asc' in filter_query.sort
        or 'user_watchlist_added_at_desc' in filter_query.sort
    )
    if filter_query.user_watchlist is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()

    if filter_query.user_watchlist or has_sort:
        query = query.where(
            MMovieWatchlist.user_id == filter_query.user.id,
            MMovieWatchlist.movie_id == MMovie.id,
        )
    elif not filter_query.user_watchlist:
        query = query.join(
            MMovieWatchlist,
            sa.and_(
                MMovieWatchlist.user_id == filter_query.user.id,
                MMovieWatchlist.movie_id == MMovie.id,
            ),
            isouter=True,
        ).where(
            MMovieWatchlist.movie_id is None,
        )
    return query
