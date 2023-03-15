from ... import schemas
from .... import utils
from ...expand.series import expand_series
from .query_filter_schema import Series_query_filter
from .user_watchlist import filter_user_watchlist
from .user_favorites import filter_user_favorites
from .user_can_watch import filter_user_can_watch
from .user_has_watched import filter_has_watched
from .genres import filter_genres
from .order import order_query


async def filter_series(
    session, 
    query: any, 
    filter_query: Series_query_filter, 
    page_cursor: schemas.Page_cursor_query,
    can_watch_episode_number: any = None,
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
    p.items = [schemas.Series.from_orm(row[0]) for row in p.items]
    await expand_series(
        series=p.items,
        user=filter_query.user,
        expand=filter_query.expand,
        session=session,
    )
    return p


def filter_series_query(query: any, filter_query: Series_query_filter, can_watch_episode_number: any = None):
    query = filter_user_watchlist(query, filter_query)
    query = filter_user_favorites(query, filter_query)
    query = filter_user_can_watch(query, filter_query, episode_number=can_watch_episode_number)
    query = filter_has_watched(query, filter_query)
    query = filter_genres(query, filter_query)
    query = order_query(query, filter_query)
    return query
