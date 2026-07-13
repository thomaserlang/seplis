from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.movie_model import MMovie, MMovieWatched
from ..types.movie_filter_types import MovieQueryFilter


def filter_user_has_watched(query: Any, filter_query: MovieQueryFilter) -> Any:
    has_sort = (
        'user_last_watched_at_asc' in filter_query.sort
        or 'user_last_watched_at_desc' in filter_query.sort
    )
    if filter_query.user_has_watched is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()

    if filter_query.user_has_watched or has_sort:
        query = query.where(
            MMovieWatched.user_id == filter_query.user.id,
            MMovieWatched.movie_id == MMovie.id,
        )
    elif not filter_query.user_has_watched:
        query = query.join(
            MMovieWatched,
            sa.and_(
                MMovieWatched.user_id == filter_query.user.id,
                MMovieWatched.movie_id == MMovie.id,
            ),
            isouter=True,
        ).where(
            MMovieWatched.movie_id is None,
        )
    return query
