from typing import Any

from ..models.series_model import MSeries
from ..types.series_filter_types import SeriesQueryFilter


def filter_language(query: Any, filter_query: SeriesQueryFilter) -> Any:
    if filter_query.language:
        query = query.where(
            MSeries.language.in_(filter_query.language),
        )
    return query
