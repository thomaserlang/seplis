from .query_filter_schema import Movie_query_filter
from ... import exceptions, models


def filter_can_watch(query, filter_query: Movie_query_filter):
    has_sort = ('user_play_server_movie_added_asc' in filter_query.sort or 
                'user_play_server_movie_added_desc' in filter_query.sort)
    if not filter_query.user_can_watch and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return query.where(
        models.Play_server_access.user_id == filter_query.user.id,
        models.Play_server_movie.play_server_id == models.Play_server_access.play_server_id,
        models.Play_server_movie.movie_id == models.Movie.id,
    )