from ... import models
from .query_filter_schema import Movie_query_filter


def filter_language(query, filter_query: Movie_query_filter):
    if filter_query.language:
        query = query.where(
            models.MMovie.language.in_(filter_query.language),
        )
    return query
