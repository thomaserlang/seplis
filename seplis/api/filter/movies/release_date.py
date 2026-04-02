from ... import models
from .query_filter_schema import Movie_query_filter


def filter_release_date(query, filter_query: Movie_query_filter):
    if filter_query.release_date_gt:
        query = query.where(
            models.MMovie.release_date >= filter_query.release_date_gt,
        )
    
    if filter_query.release_date_lt:
        query = query.where(
            models.MMovie.release_date <= filter_query.release_date_lt,
        )

    return query