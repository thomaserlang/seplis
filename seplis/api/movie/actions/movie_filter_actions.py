from typing import Any, cast

from sqlalchemy.engine import RowMapping

from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor

from ..models.movie_model import MMovie
from ..schemas.movie_schemas import Movie
from ..types.movie_filter_types import MovieQueryFilter
from .movie_expand_actions import expand_movies
from .movie_genre_filter_actions import filter_genres
from .movie_language_filter_actions import filter_language
from .movie_mapping import movie_row_mapper
from .movie_order_actions import order_query
from .movie_rating_filter_actions import filter_rating
from .movie_release_date_filter_actions import filter_release_date
from .movie_user_can_watch_filter_actions import filter_can_watch
from .movie_user_favorite_filter_actions import filter_user_favorites
from .movie_user_watched_filter_actions import filter_user_has_watched
from .movie_user_watchlist_filter_actions import filter_user_watchlist


def movie_filter_mapper(row: RowMapping) -> Movie:
    return movie_row_mapper(row)


async def filter_movies(
    session: Any,
    query: Any,
    filter_query: MovieQueryFilter,
    page_query: PageCursorQuery,
) -> PageCursor[Movie]:
    p = await page_cursor(
        query=filter_movies_query(query, filter_query),
        page_query=page_query,
        session=session,
        count_total=False,
        record_mapper=movie_filter_mapper,
    )
    await expand_movies(
        movies=p.records,
        user=filter_query.user,
        expand=cast(list[str] | None, filter_query.expand),
    )
    return p


def filter_movies_query(query: Any, filter_query: MovieQueryFilter) -> Any:
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
        query = query.where(MMovie.collection_id.in_(filter_query.collection_id))
    return query
