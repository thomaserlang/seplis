from typing import Any

from ..models.movie_model import MMovie
from ..types.movie_filter_types import MovieQueryFilter


def filter_language(query: Any, filter_query: MovieQueryFilter) -> Any:
    if filter_query.language:
        query = query.where(
            MMovie.language.in_(filter_query.language),
        )
    return query
