import sqlalchemy as sa

from ... import models
from .query_filter_schema import Movie_query_filter


def filter_genres(query, filter_query: Movie_query_filter):
    if filter_query.genre_id:
        query = query.where(
            models.MMovieGenre.genre_id.in_(filter_query.genre_id),
            models.MMovie.id == models.MMovieGenre.movie_id,
        ).group_by(models.MMovie.id)

    if filter_query.not_genre_id:
        genre = sa.orm.aliased(models.MMovieGenre)
        query = query.join(
            genre,
            sa.and_(
                genre.movie_id == models.MMovie.id,
                genre.genre_id.in_(filter_query.not_genre_id),
            ),
            isouter=True,
        ).where(
            genre.movie_id is None,
        )

    return query