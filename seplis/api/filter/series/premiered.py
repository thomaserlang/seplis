from ... import models
from .query_filter_schema import Series_query_filter


def filter_premiered(query, filter_query: Series_query_filter):
    if filter_query.premiered_gt:
        query = query.where(
            models.MSeries.premiered >= filter_query.premiered_gt,
        )

    if filter_query.premiered_lt:
        query = query.where(
            models.MSeries.premiered <= filter_query.premiered_lt,
        )
    
    return query