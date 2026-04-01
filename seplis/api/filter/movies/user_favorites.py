import sqlalchemy as sa

from ... import exceptions, models
from .query_filter_schema import Movie_query_filter


def filter_user_favorites(query, filter_query: Movie_query_filter):
    has_sort = ('user_favorites_added_at_asc' in filter_query.sort or
                'user_favorites_added_at_desc' in filter_query.sort)
    if filter_query.user_favorites is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()

    if filter_query.user_favorites or has_sort:
        query = query.where(
            models.Movie_favorite.user_id == filter_query.user.id,
            models.Movie_favorite.movie_id == models.Movie.id,
        )
    elif not filter_query.user_favorites:
        query = query.join(
            models.Movie_favorite,
            sa.and_(
                models.Movie_favorite.user_id == filter_query.user.id,
                models.Movie_favorite.movie_id == models.Movie.id,
            ),
            isouter=True,
        ).where(
            models.Movie_favorite.movie_id is None,
        )
    return query