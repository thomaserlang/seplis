import sqlalchemy as sa

from ... import exceptions, models
from .query_filter_schema import Movie_query_filter


def filter_user_has_watched(query, filter_query: Movie_query_filter):
    has_sort = (
        'user_last_watched_at_asc' in filter_query.sort
        or 'user_last_watched_at_desc' in filter_query.sort
    )
    if filter_query.user_has_watched is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()

    if filter_query.user_has_watched or has_sort:
        query = query.where(
            models.MMovieWatched.user_id == filter_query.user.id,
            models.MMovieWatched.movie_id == models.MMovie.id,
        )
    elif not filter_query.user_has_watched:
        query = query.join(
            models.MMovieWatched,
            sa.and_(
                models.MMovieWatched.user_id == filter_query.user.id,
                models.MMovieWatched.movie_id == models.MMovie.id,
            ),
            isouter=True,
        ).where(
            models.MMovieWatched.movie_id is None,
        )
    return query
