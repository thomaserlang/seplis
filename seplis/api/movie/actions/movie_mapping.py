from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.genre import Genre
from seplis.api.image import image_columns, image_mapper
from seplis.api.image.models.image_model import MImage

from ..models.movie_collection_model import MMovieCollection
from ..models.movie_model import MMovie
from ..schemas.movie_collection_schemas import MovieCollection
from ..schemas.movie_schemas import Movie


def select_movies() -> sa.Select[Any]:
    return (
        sa.select(
            MMovie.__table__,
            *image_columns(),
            MMovieCollection.id.label('collection_result_id'),
            MMovieCollection.name.label('collection_result_name'),
        )
        .outerjoin(MImage.__table__, MImage.id == MMovie.poster_image_id)
        .outerjoin(
            MMovieCollection.__table__,
            MMovieCollection.id == MMovie.collection_id,
        )
    )


def movie_row_mapper(movie: RowMapping) -> Movie:
    popularity = movie['popularity']
    rating = movie['rating']

    collection = None
    if movie['collection_result_id'] is not None:
        collection = MovieCollection(
            id=movie['collection_result_id'],
            name=movie['collection_result_name'] or '',
        )

    return Movie(
        id=movie['id'],
        poster_image=image_mapper(movie, 'image_') if movie['image_id'] else None,
        title=movie['title'],
        original_title=movie['original_title'],
        alternative_titles=list(movie['alternative_titles'] or []),
        status=movie['status'],
        plot=movie['plot'],
        tagline=movie['tagline'],
        externals=dict(movie['externals'] or {}),
        language=movie['language'],
        runtime=movie['runtime'],
        release_date=movie['release_date'],
        budget=movie['budget'],
        revenue=movie['revenue'],
        popularity=float(popularity) if popularity is not None else None,
        rating=float(rating) if rating is not None else None,
        rating_votes=movie['rating_votes'],
        genres=[
            value
            if isinstance(value, Genre)
            else Genre(
                id=int(value.get('id') or 0),
                name=str(value.get('name') or ''),
                number_of=int(value.get('number_of') or 0),
            )
            for value in movie['genres'] or []
        ],
        collection=collection,
    )
