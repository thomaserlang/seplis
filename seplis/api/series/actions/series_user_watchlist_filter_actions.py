from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.series_model import MSeries
from ..models.series_watchlist_model import MSeriesWatchlist
from ..types.series_filter_types import SeriesQueryFilter


def filter_user_watchlist(query: Any, filter_query: SeriesQueryFilter) -> Any:
    has_sort = (
        'user_watchlist_added_at_asc' in filter_query.sort
        or 'user_watchlist_added_at_desc' in filter_query.sort
    )
    if filter_query.user_watchlist is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()
    return filter_user_watchlist_query(
        query=query,
        user_watchlist=filter_query.user_watchlist or has_sort,
        user_id=filter_query.user.id,
    )


def filter_user_watchlist_query(query: Any, user_watchlist: bool, user_id: Any) -> Any:

    if user_watchlist:
        query = query.where(
            MSeriesWatchlist.user_id == user_id,
            MSeriesWatchlist.series_id == MSeries.id,
        )
    elif not user_watchlist:
        query = query.where(
            sa.not_(
                sa.exists(
                    sa.select(1).where(
                        MSeriesWatchlist.user_id == user_id,
                        MSeriesWatchlist.series_id == MSeries.id,
                    )
                )
            )
        )
    return query
