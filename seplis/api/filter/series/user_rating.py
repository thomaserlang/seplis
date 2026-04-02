import sqlalchemy as sa

from ... import exceptions, models
from .query_filter_schema import Series_query_filter


def filter_user_rating(query: any, filter_query: Series_query_filter):
    has_sort = ('user_rating_asc' in filter_query.sort or 
                'user_rating_desc' in filter_query.sort)
    if not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return filter_user_rating_query(query, filter_query.user.id)


def filter_user_rating_query(query: any, user_id: int):
    return query.join(
        models.MSeriesUserRating,
        sa.and_(
            models.MSeriesUserRating.user_id == user_id,
            models.MSeries.id == models.MSeriesUserRating.series_id,
        ),
        isouter=True,
    )