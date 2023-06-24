from ...expand.movie import expand_movies
from ... import schemas, models
from .... import utils
from .query_filter_schema import Movie_query_filter
from .user_watchlist import filter_user_watchlist
from .user_has_watched import filter_user_has_watched
from .order import order_query
from .genres import filter_genres
from .user_can_watch import filter_can_watch
from .user_favorites import filter_user_favorites


async def filter_movies(session, query: any, filter_query: Movie_query_filter, page_cursor: schemas.Page_cursor_query):
    p = await utils.sqlalchemy.paginate_cursor(
        query=filter_movies_query(query, filter_query),
        page_query=page_cursor,
        session=session,
    )
    p.items = [schemas.Movie.from_orm(row[0]) for row in p.items]
    await expand_movies(
        movies=p.items,
        user=filter_query.user,
        expand=filter_query.expand,
    )
    return p


def filter_movies_query(query: any, filter_query: Movie_query_filter):
    query = filter_user_watchlist(query, filter_query)
    query = filter_user_favorites(query, filter_query)
    query = filter_user_has_watched(query, filter_query)
    query = filter_genres(query, filter_query)
    query = filter_can_watch(query, filter_query)
    query = order_query(query, filter_query)
    if filter_query.collection_id:
        query = query.where(models.Movie.collection_id.in_(filter_query.collection_id))
    return query
