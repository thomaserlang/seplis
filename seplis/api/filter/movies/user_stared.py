import sqlalchemy as sa
from .query_filter_schema import Movie_query_filter
from ... import exceptions, models


def filter_user_stared(query, filter_query: Movie_query_filter):
    has_sort = ('user_stared_at_asc' in filter_query.sort or
                'user_stared_at_desc' in filter_query.sort)
    if filter_query.user_stared == None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()

    if filter_query.user_stared == True or has_sort:
        query = query.where(
            models.Movie_stared.user_id == filter_query.user.id,
            models.Movie_stared.movie_id == models.Movie.id,
        )
    elif filter_query.user_stared == False:
        query = query.join(
            models.Movie_stared,
            sa.and_(
                models.Movie_stared.user_id == filter_query.user.id,
                models.Movie_stared.movie_id == models.Movie.id,
            ),
            isouter=True,
        ).where(
            models.Movie_stared.movie_id == None,
        )
    return query