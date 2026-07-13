from datetime import date, datetime
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis.api.genre import Genre, genre_mapper
from seplis.api.image import image_mapper
from seplis.api.image.models.image_model import MImage
from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime

from ..schemas.movie_collection_schemas import MovieCollection
from ..schemas.movie_schemas import Movie
from .movie_collection_model import MMovieCollection


class MMovie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str | None] = mapped_column(sa.String(200))
    original_title: Mapped[str | None] = mapped_column(sa.String(200))
    alternative_titles: Mapped[list | None] = mapped_column(sa.JSON)
    externals: Mapped[dict | None] = mapped_column(sa.JSON)
    created_at: Mapped[datetime | None] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime | None] = mapped_column(UtcDateTime)
    status: Mapped[int | None] = mapped_column(sa.SmallInteger)
    plot: Mapped[str | None] = mapped_column(sa.String(2000))
    tagline: Mapped[str | None] = mapped_column(sa.String(500))
    language: Mapped[str | None] = mapped_column(sa.String(20))
    poster_image_id: Mapped[int | None] = mapped_column(sa.ForeignKey('images.id'))
    poster_image: Mapped[MImage | None] = relationship('MImage', lazy=False)
    runtime: Mapped[int | None] = mapped_column()
    release_date: Mapped[date | None] = mapped_column(sa.Date)
    budget: Mapped[int | None] = mapped_column(sa.BIGINT)
    revenue: Mapped[int | None] = mapped_column(sa.BIGINT)
    genres: Mapped[list | None] = mapped_column(sa.JSON(), default=lambda: [])
    popularity: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(precision=12, scale=4))
    rating: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(4, 2))
    rating_votes: Mapped[int | None] = mapped_column()
    rating_weighted: Mapped[Decimal] = mapped_column(
        sa.DECIMAL(precision=12, scale=4), server_default='0'
    )
    collection_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('movie_collections.id')
    )
    collection: Mapped[MMovieCollection | None] = relationship(
        'MMovieCollection', lazy=False
    )


class MMovieExternal(Base):
    __tablename__ = 'movie_externals'

    movie_id: Mapped[int] = mapped_column(
        sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False
    )
    title: Mapped[str] = mapped_column(sa.String(45), primary_key=True)
    value: Mapped[str | None] = mapped_column(sa.String(45))


class MMovieWatched(Base):
    __tablename__ = 'movies_watched'
    __serialize_ignore__ = (
        'movie_id',
        'user_id',
    )

    movie_id: Mapped[int] = mapped_column(
        sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey('users.id'), primary_key=True, autoincrement=False
    )
    times: Mapped[int | None] = mapped_column(sa.SmallInteger)
    position: Mapped[int | None] = mapped_column(sa.SmallInteger)
    watched_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MMovieWatchedHistory(Base):
    __tablename__ = 'movies_watched_history'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    movie_id: Mapped[int | None] = mapped_column(sa.ForeignKey('movies.id'))
    user_id: Mapped[int | None] = mapped_column(sa.ForeignKey('users.id'))
    watched_at: Mapped[datetime | None] = mapped_column(UtcDateTime)


class MMovieGenre(Base):
    __tablename__ = 'movie_genres'

    movie_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    genre_id: Mapped[int] = mapped_column(
        sa.ForeignKey('genres.id', ondelete='cascade', onupdate='cascade'),
        primary_key=True,
        autoincrement=False,
    )


def movie_collection_mapper(collection: MMovieCollection) -> MovieCollection:
    return MovieCollection(
        id=collection.id,
        name=collection.name or '',
    )


def genre_from_value(value: Any) -> Genre:
    if isinstance(value, Genre):
        return value
    if isinstance(value, dict):
        return Genre(
            id=int(value.get('id') or 0),
            name=str(value.get('name') or ''),
            number_of=int(value.get('number_of') or 0),
        )
    return genre_mapper(value)


def genres_from_values(values: list[Any] | None) -> list[Genre]:
    return [genre_from_value(value) for value in values or []]


def movie_mapper(movie: MMovie) -> Movie:
    return Movie(
        id=movie.id,
        poster_image=image_mapper(movie.poster_image) if movie.poster_image else None,
        title=movie.title,
        original_title=movie.original_title,
        alternative_titles=list(movie.alternative_titles or []),
        status=movie.status,
        plot=movie.plot,
        tagline=movie.tagline,
        externals=dict(movie.externals or {}),
        language=movie.language,
        runtime=movie.runtime,
        release_date=movie.release_date,
        budget=movie.budget,
        revenue=movie.revenue,
        popularity=float(movie.popularity) if movie.popularity is not None else None,
        rating=float(movie.rating) if movie.rating is not None else None,
        rating_votes=movie.rating_votes,
        genres=genres_from_values(movie.genres),
        collection=movie_collection_mapper(movie.collection)
        if movie.collection
        else None,
    )
