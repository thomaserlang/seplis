from ...expand.movie import expand_movies
from ... import schemas
from .... import utils
from .query_filter_schema import Movie_query_filter
from .user_stared import filter_user_stared
from .user_has_watched import filter_user_has_watched
from .order import order_query
from .genres import filter_genres
from .user_can_watch import filter_can_watch


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
        session=session,
    )
    return p


def filter_movies_query(query: any, filter_query: Movie_query_filter):
    query = filter_user_stared(query, filter_query)
    query = filter_user_has_watched(query, filter_query)
    query = filter_genres(query, filter_query)
    query = filter_can_watch(query, filter_query)
    query = order_query(query, filter_query)
    return query
