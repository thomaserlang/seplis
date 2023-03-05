import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from ... import exceptions, models


def filter_user_following(query, filter_query: Series_query_filter):
    has_sort = ('user_followed_at_asc' in filter_query.sort or 
                'user_followed_at_desc' in filter_query.sort)
    if filter_query.user_following == None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return filter_user_following_query(
        query=query, 
        user_following=filter_query.user_following or has_sort,
        user_id=filter_query.user.id,
    )


def filter_user_following_query(query, user_following: bool, user_id: any):
    if user_following == True:
        query = query.where(
            models.Series_follower.user_id == user_id,
            models.Series_follower.series_id == models.Series.id,
        )
    elif user_following == False:
        query = query.join(
            models.Series_follower,
            sa.and_(
                models.Series_follower.user_id == user_id,
                models.Series_follower.series_id == models.Series.id,
            ),
            isouter=True,
        ).where(
            models.Series_follower.series_id == None,
        )
    return query