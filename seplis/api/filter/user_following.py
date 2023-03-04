import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from .. import exceptions, models


def filter_user_following(query, filter_query: Series_query_filter):
    if filter_query.user_following == None:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()

    if filter_query.user_following == True or filter_query.sort.startswith('user_followed_at'):
        query = query.where(
            models.Series_follower.user_id == filter_query.user.id,
            models.Series_follower.series_id == models.Series.id,
        )
    elif filter_query.user_following == False:
        query = query.join(
            models.Series_follower,
            sa.and_(
                models.Series_follower.user_id == filter_query.user.id,
                models.Series_follower.series_id == models.Series.id,
            ),
            isouter=True,
        ).where(
            models.Series_follower.series_id == None,
        )
    return query