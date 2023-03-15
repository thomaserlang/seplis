import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from ... import exceptions, models


def filter_user_watchlist(query, filter_query: Series_query_filter):
    has_sort = ('user_watchlist_added_at_asc' in filter_query.sort or 
                'user_watchlist_added_at_desc' in filter_query.sort)
    if filter_query.user_watchlist == None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return filter_user_watchlist_query(
        query=query, 
        user_watchlist=filter_query.user_watchlist or has_sort,
        user_id=filter_query.user.id,
    )


def filter_user_watchlist_query(query, user_watchlist: bool, user_id: any):
    if user_watchlist == True:
        query = query.where(
            models.Series_watchlist.user_id == user_id,
            models.Series_watchlist.series_id == models.Series.id,
        )
    elif user_watchlist == False:
        query = query.join(
            models.Series_watchlist,
            sa.and_(
                models.Series_watchlist.user_id == user_id,
                models.Series_watchlist.series_id == models.Series.id,
            ),
            isouter=True,
        ).where(
            models.Series_watchlist.series_id == None,
        )
    return query