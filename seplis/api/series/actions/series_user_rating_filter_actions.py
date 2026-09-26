from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.series_model import MSeries
from ..models.series_user_rating_model import MSeriesUserRating
from ..types.series_filter_types import SeriesQueryFilter


def filter_user_rating(query: Any, filter_query: SeriesQueryFilter) -> Any:
    has_sort = (
        'user_rating_asc' in filter_query.sort or 'user_rating_desc' in filter_query.sort
    )
    if not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()
    return filter_user_rating_query(query, filter_query.user.id)


def filter_user_rating_query(query: Any, user_id: int) -> Any:
    return query.join(
        MSeriesUserRating.__table__,
        sa.and_(
            MSeriesUserRating.user_id == user_id,
            MSeries.id == MSeriesUserRating.series_id,
        ),
        isouter=True,
    )
