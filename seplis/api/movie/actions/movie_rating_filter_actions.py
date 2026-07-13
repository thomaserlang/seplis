from typing import Any

from ..models.movie_model import MMovie
from ..types.movie_filter_types import MovieQueryFilter


def filter_rating(query: Any, filter_query: MovieQueryFilter) -> Any:
    if filter_query.rating_gt and filter_query.rating_gt > 0:
        query = query.where(
            MMovie.rating >= filter_query.rating_gt,
        )

    if filter_query.rating_lt and filter_query.rating_lt < 10:
        query = query.where(
            MMovie.rating <= filter_query.rating_lt,
        )

    if filter_query.rating_votes_gt:
        query = query.where(
            MMovie.rating_votes >= filter_query.rating_votes_gt,
        )

    return query
