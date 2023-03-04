from .query_filter_schema import Movie_query_filter
from ... import models


def filter_genres(query, filter_query: Movie_query_filter):
    if not filter_query.genre_id:
        return query

    if len(filter_query.genre_id) == 1:
        query = query.where(
            models.Movie_genre.genre_id == filter_query.genre_id[0],
            models.Movie.id == models.Movie_genre.movie_id,
        )
    else:
        query = query.where(
            models.Movie_genre.genre_id.in_(filter_query.genre_id),
            models.Movie.id == models.Movie_genre.movie_id,
        ).group_by(models.Movie.id)
    return query