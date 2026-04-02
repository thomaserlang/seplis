from typing import Any

import sqlalchemy as sa

from ... import exceptions, models
from .query_filter_schema import Series_query_filter


def filter_user_favorites(query, filter_query: Series_query_filter):
    has_sort = (
        'user_favorite_added_at_asc' in filter_query.sort
        or 'user_favorite_added_at_desc' in filter_query.sort
    )
    if filter_query.user_favorites is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return filter_user_favorites_query(
        query=query,
        user_favorites=filter_query.user_favorites or has_sort,
        user_id=filter_query.user.id,
    )


def filter_user_favorites_query(query, user_favorites: bool, user_id: Any):
    if user_favorites:
        query = query.where(
            models.MSeriesFavorite.user_id == user_id,
            models.MSeriesFavorite.series_id == models.MSeries.id,
        )
    elif not user_favorites:
        query = query.join(
            models.MSeriesFavorite,
            sa.and_(
                models.MSeriesFavorite.user_id == user_id,
                models.MSeriesFavorite.series_id == models.MSeries.id,
            ),
            isouter=True,
        ).where(
            models.MSeriesFavorite.series_id is None,
        )
    return query
