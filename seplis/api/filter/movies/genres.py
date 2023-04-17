import sqlalchemy as sa
from .query_filter_schema import Movie_query_filter
from ... import models


def filter_genres(query, filter_query: Movie_query_filter):
    if filter_query.genre_id:
        query = query.where(
            models.Movie_genre.genre_id.in_(filter_query.genre_id),
            models.Movie.id == models.Movie_genre.movie_id,
        ).group_by(models.Movie.id)

    if filter_query.not_genre_id:
        genre = sa.orm.aliased(models.Movie_genre)
        query = query.join(
            genre,
            sa.and_(
                genre.movie_id == models.Movie.id,
                genre.genre_id.in_(filter_query.not_genre_id),
            ),
            isouter=True,
        ).where(
            genre.movie_id == None,
        )

    return query