from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.movie_favorite_model import MMovieFavorite
from ..models.movie_model import MMovie
from ..types.movie_filter_types import MovieQueryFilter


def filter_user_favorites(query: Any, filter_query: MovieQueryFilter) -> Any:
    has_sort = (
        'user_favorites_added_at_asc' in filter_query.sort
        or 'user_favorites_added_at_desc' in filter_query.sort
    )
    if filter_query.user_favorites is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()

    if filter_query.user_favorites or has_sort:
        query = query.where(
            MMovieFavorite.user_id == filter_query.user.id,
            MMovieFavorite.movie_id == MMovie.id,
        )
    elif not filter_query.user_favorites:
        query = query.join(
            MMovieFavorite,
            sa.and_(
                MMovieFavorite.user_id == filter_query.user.id,
                MMovieFavorite.movie_id == MMovie.id,
            ),
            isouter=True,
        ).where(
            MMovieFavorite.movie_id is None,
        )
    return query
