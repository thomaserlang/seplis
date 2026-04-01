from typing import Any

from .... import utils
from ... import schemas
from ...expand.series import expand_series
from .genres import filter_genres
from .language import filter_language
from .order import order_query
from .premiered import filter_premiered
from .query_filter_schema import Series_query_filter
from .rating import filter_rating
from .user_can_watch import filter_user_can_watch
from .user_favorites import filter_user_favorites
from .user_has_watched import filter_has_watched
from .user_rating import filter_user_rating
from .user_watchlist import filter_user_watchlist


async def filter_series(
    session: Any,
    query: Any,
    filter_query: Series_query_filter,
    page_cursor: schemas.Page_cursor_query,
    can_watch_episode_number: Any = None,
):
    p = await utils.sqlalchemy.paginate_cursor(
        query=filter_series_query(
            query,
            filter_query,
            can_watch_episode_number=can_watch_episode_number,
        ),
        page_query=page_cursor,
        session=session,
    )
    p.items = [schemas.Series.model_validate(row[0]) for row in p.items]
    await expand_series(
        series=p.items,
        user=filter_query.user,
        expand=filter_query.expand,
    )
    return p


def filter_series_query(
    query: Any, filter_query: Series_query_filter, can_watch_episode_number: Any = None
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
