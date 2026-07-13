from typing import Any

from ..models.series_model import MSeries
from ..types.series_filter_types import SeriesQueryFilter


def filter_premiered(query: Any, filter_query: SeriesQueryFilter) -> Any:
    if filter_query.premiered_gt:
        query = query.where(
            MSeries.premiered >= filter_query.premiered_gt,
        )

    if filter_query.premiered_lt:
        query = query.where(
            MSeries.premiered <= filter_query.premiered_lt,
        )

    return query
