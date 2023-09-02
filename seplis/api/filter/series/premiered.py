import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from ... import models


def filter_premiered(query, filter_query: Series_query_filter):
    if filter_query.premiered_gt:
        query = query.where(
            models.Series.premiered >= filter_query.premiered_gt,
        )

    if filter_query.premiered_lt:
        query = query.where(
            models.Series.premiered <= filter_query.premiered_lt,
        )
    
    return query