from .... import utils
from ... import models, schemas
from ...expand.movie import expand_movies
from .genres import filter_genres
from .language import filter_language
from .order import order_query
from .query_filter_schema import Movie_query_filter
from .rating import filter_rating
from .release_date import filter_release_date
from .user_can_watch import filter_can_watch
from .user_favorites import filter_user_favorites
from .user_has_watched import filter_user_has_watched
from .user_watchlist import filter_user_watchlist


async def filter_movies(session, query: any, filter_query: Movie_query_filter, page_cursor: schemas.Page_cursor_query):
    p = await utils.sqlalchemy.paginate_cursor(
        query=filter_movies_query(query, filter_query),
        page_query=page_cursor,
        session=session,
    )
    p.items = [schemas.Movie.model_validate(row[0]) for row in p.items]
    await expand_movies(
        movies=p.items,
        user=filter_query.user,
        expand=filter_query.expand,
    )
    return p


def filter_movies_query(query: any, filter_query: Movie_query_filter):
    query = filter_release_date(query, filter_query)
    query = filter_user_watchlist(query, filter_query)
    query = filter_user_favorites(query, filter_query)
    query = filter_user_has_watched(query, filter_query)
    query = filter_genres(query, filter_query)
    query = filter_can_watch(query, filter_query)
    query = filter_rating(query, filter_query)
    query = filter_language(query, filter_query)
    query = order_query(query, filter_query)
    if filter_query.collection_id:
        query = query.where(models.MMovie.collection_id.in_(filter_query.collection_id))
    return query
