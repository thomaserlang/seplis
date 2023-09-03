import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from ... import models


def filter_rating(query, filter_query: Series_query_filter):
    if filter_query.rating_gt and filter_query.rating_gt > 0:
        query = query.where(
            models.Series.rating >= filter_query.rating_gt,
        )

    if filter_query.rating_lt and filter_query.rating_lt < 10:
        query = query.where(
            models.Series.rating <= filter_query.rating_lt,
        )

    if filter_query.rating_votes_gt and filter_query.rating_votes_gt > 0:
        query = query.where(
            models.Series.rating_votes >= filter_query.rating_votes_gt,
        )
    
    return query