import sqlalchemy as sa
from .. import schemas, models
from ... import utils
from ..expand.series import expand_series
from .query_filter_schema import Series_query_filter
from .user_following import filter_user_following
from .user_can_watch import filter_can_watch
from .user_has_watched import filter_has_watched
from .genres import filter_genres


async def filter_series(session, query: any, filter_query: Series_query_filter, page_cursor: schemas.Page_cursor_query):
    query = series_filter_query(query, filter_query)

    p = await utils.sqlalchemy.paginate_cursor(
        session=session,
        query=query,
        page_query=page_cursor,
    )
    p.items = [schemas.Series.from_orm(row[0]) for row in p.items]
    await expand_series(series=p.items, user=filter_query.user, expand=filter_query.expand, session=session)
    return p


def series_filter_query(query: any, filter_query: Series_query_filter):
    query = filter_user_following(query, filter_query)
    query = filter_can_watch(query, filter_query)
    query = filter_has_watched(query, filter_query)
    query = filter_genres(query, filter_query)

    direction = sa.asc if filter_query.sort.endswith('_asc') else sa.desc
    if filter_query.sort.startswith('user_rating'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series_user_rating.rating, -1)),
            direction(models.Series.id),
        )
    elif filter_query.sort.startswith('user_followed_at') and filter_query.user_following != False:
        query = query.order_by(
            direction(sa.func.coalesce(models.Series_follower.created_at, -1)),
            direction(models.Series.id),
        )
    elif filter_query.sort.startswith('user_last_episode_watched_at') and filter_query.user_has_watched != False:
        query = query.order_by(
            direction(sa.func.coalesce(models.Episode_watched.watched_at, -1)),
            direction(models.Series.id),
        )
    elif filter_query.sort.startswith('rating'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series.rating, -1)),
            direction(models.Series.id),
        )
    elif filter_query.sort.startswith('popularity_desc'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series.popularity, -1)),
            direction(models.Series.id),
        )
    else:
        query = query.order_by(
            direction(sa.func.coalesce(models.Series.popularity, -1)),
            direction(models.Series.id),
        )
    return query
