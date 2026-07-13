from typing import Any

from ..models.series_model import MSeries
from ..types.series_filter_types import SeriesQueryFilter


def filter_rating(query: Any, filter_query: SeriesQueryFilter) -> Any:
    if filter_query.rating_gt and filter_query.rating_gt > 0:
        query = query.where(
            MSeries.rating >= filter_query.rating_gt,
        )

    if filter_query.rating_lt and filter_query.rating_lt < 10:
        query = query.where(
            MSeries.rating <= filter_query.rating_lt,
        )

    if filter_query.rating_votes_gt and filter_query.rating_votes_gt > 0:
        query = query.where(
            MSeries.rating_votes >= filter_query.rating_votes_gt,
        )

    return query
