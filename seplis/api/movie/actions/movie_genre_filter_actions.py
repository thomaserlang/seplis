from typing import Any

import sqlalchemy as sa

from ..models.movie_model import MMovie, MMovieGenre
from ..types.movie_filter_types import MovieQueryFilter


def filter_genres(query: Any, filter_query: MovieQueryFilter) -> Any:
    if filter_query.genre_id:
        query = query.where(
            MMovieGenre.genre_id.in_(filter_query.genre_id),
            MMovie.id == MMovieGenre.movie_id,
        ).group_by(MMovie.id)

    if filter_query.not_genre_id:
        genre = MMovieGenre.__table__.alias()
        query = query.join(
            genre,
            sa.and_(
                genre.c.movie_id == MMovie.id,
                genre.c.genre_id.in_(filter_query.not_genre_id),
            ),
            isouter=True,
        ).where(
            genre.c.movie_id.is_(None),
        )

    return query
