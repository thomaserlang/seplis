from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import aliased

from ..models.movie_model import MMovie, MMovieGenre
from ..types.movie_filter_types import MovieQueryFilter


def filter_genres(query: Any, filter_query: MovieQueryFilter) -> Any:
    if filter_query.genre_id:
        query = query.where(
            MMovieGenre.genre_id.in_(filter_query.genre_id),
            MMovie.id == MMovieGenre.movie_id,
        ).group_by(MMovie.id)

    if filter_query.not_genre_id:
        genre = aliased(MMovieGenre)
        query = query.join(
            genre,
            sa.and_(
                genre.movie_id == MMovie.id,
                genre.genre_id.in_(filter_query.not_genre_id),
            ),
            isouter=True,
        ).where(
            genre.movie_id is None,
        )

    return query
