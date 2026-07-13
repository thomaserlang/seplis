from typing import Any

from ..models.movie_model import MMovie
from ..types.movie_filter_types import MovieQueryFilter


def filter_release_date(query: Any, filter_query: MovieQueryFilter) -> Any:
    if filter_query.release_date_gt:
        query = query.where(
            MMovie.release_date >= filter_query.release_date_gt,
        )

    if filter_query.release_date_lt:
        query = query.where(
            MMovie.release_date <= filter_query.release_date_lt,
        )

    return query
