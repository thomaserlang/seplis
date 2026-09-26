from typing import Any, cast

from sqlalchemy.engine import RowMapping

from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor

from ..schemas.series_schemas import Series
from ..types.series_filter_types import SeriesQueryFilter
from .series_expand_actions import expand_series
from .series_genre_filter_actions import filter_genres
from .series_language_filter_actions import filter_language
from .series_mapping import series_row_mapper
from .series_order_actions import order_query
from .series_premiered_filter_actions import filter_premiered
from .series_rating_filter_actions import filter_rating
from .series_user_can_watch_filter_actions import filter_user_can_watch
from .series_user_favorite_filter_actions import filter_user_favorites
from .series_user_rating_filter_actions import filter_user_rating
from .series_user_watched_filter_actions import filter_has_watched
from .series_user_watchlist_filter_actions import filter_user_watchlist


def series_filter_mapper(row: RowMapping) -> Series:
    return series_row_mapper(row)


async def filter_series(
    session: Any,
    query: Any,
    filter_query: SeriesQueryFilter,
    page_query: PageCursorQuery,
    can_watch_episode_number: Any = None,
) -> PageCursor[Series]:
    p = await page_cursor(
        query=filter_series_query(
            query,
            filter_query,
            can_watch_episode_number=can_watch_episode_number,
        ),
        page_query=page_query,
        session=session,
        count_total=False,
        record_mapper=series_filter_mapper,
    )
    await expand_series(
        series=p.records,
        user=filter_query.user,
        expand=cast(list[str] | None, filter_query.expand),
    )
    return p


def filter_series_query(
    query: Any, filter_query: SeriesQueryFilter, can_watch_episode_number: Any = None
) -> Any:
    query = filter_premiered(query, filter_query)
    query = filter_user_watchlist(query, filter_query)
    query = filter_user_favorites(query, filter_query)
    query = filter_user_can_watch(
        query, filter_query, episode_number=can_watch_episode_number
    )
    query = filter_has_watched(query, filter_query)
    query = filter_genres(query, filter_query)
    query = filter_user_rating(query, filter_query)
    query = filter_rating(query, filter_query)
    query = filter_language(query, filter_query)

    return order_query(query, filter_query)
