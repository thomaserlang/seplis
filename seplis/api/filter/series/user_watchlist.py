from typing import Any

import sqlalchemy as sa

from ... import exceptions, models
from .query_filter_schema import Series_query_filter


def filter_user_watchlist(query: Any, filter_query: Series_query_filter) -> Any:
    has_sort = (
        'user_watchlist_added_at_asc' in filter_query.sort
        or 'user_watchlist_added_at_desc' in filter_query.sort
    )
    if filter_query.user_watchlist is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return filter_user_watchlist_query(
        query=query,
        user_watchlist=filter_query.user_watchlist or has_sort,
        user_id=filter_query.user.id,
    )


def filter_user_watchlist_query(query: Any, user_watchlist: bool, user_id: Any) -> Any:

    if user_watchlist:
        query = query.where(
            models.Series_watchlist.user_id == user_id,
            models.Series_watchlist.series_id == models.Series.id,
        )
    elif not user_watchlist:
        query = query.where(
            sa.not_(
                sa.exists(
                    sa.select(1).where(
                        models.Series_watchlist.user_id == user_id,
                        models.Series_watchlist.series_id == models.Series.id,
                    )
                )
            )
        )
    return query
