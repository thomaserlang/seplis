from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.series_favorite_model import MSeriesFavorite
from ..models.series_model import MSeries
from ..types.series_filter_types import SeriesQueryFilter


def filter_user_favorites(query: Any, filter_query: SeriesQueryFilter) -> Any:
    has_sort = (
        'user_favorite_added_at_asc' in filter_query.sort
        or 'user_favorite_added_at_desc' in filter_query.sort
    )
    if filter_query.user_favorites is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()
    return filter_user_favorites_query(
        query=query,
        user_favorites=filter_query.user_favorites or has_sort,
        user_id=filter_query.user.id,
    )


def filter_user_favorites_query(query: Any, user_favorites: bool, user_id: Any) -> Any:
    if user_favorites:
        query = query.where(
            MSeriesFavorite.user_id == user_id,
            MSeriesFavorite.series_id == MSeries.id,
        )
    elif not user_favorites:
        query = query.join(
            MSeriesFavorite,
            sa.and_(
                MSeriesFavorite.user_id == user_id,
                MSeriesFavorite.series_id == MSeries.id,
            ),
            isouter=True,
        ).where(
            MSeriesFavorite.series_id is None,
        )
    return query
