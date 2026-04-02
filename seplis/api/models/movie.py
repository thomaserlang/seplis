from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis import utils
from seplis.utils.sqlalchemy import UtcDateTime

from ... import config
from .. import exceptions, schemas
from ..database import auto_session, database
from .base import Base
from .genre import MGenre
from .movie_collection import MMovieCollection
from .movie_watchlist import MMovieWatchlist

if TYPE_CHECKING:
    from .image import MImage


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

    @classmethod
    @auto_session
    async def save(
        cls,
        data: schemas.Movie_create | schemas.Movie_update,
        movie_id: int | None = None,
        patch=True,
        overwrite_genres=False,
        session=None,
    ):
        _data = data.model_dump(exclude_unset=True) if data else {}
        if not movie_id:
            r = await session.execute(sa.insert(MMovie))
            movie_id = r.lastrowid
            _data['created_at'] = datetime.now(tz=UTC)
        else:
            m = await session.scalar(sa.select(MMovie.id).where(MMovie.id == movie_id))
            if not m:
                raise HTTPException(404, f'Unknown movie id: {movie_id}')
            _data['updated_at'] = datetime.now(tz=UTC)
        if 'genre_names' in _data:
            _data['genres'] = await cls._save_genres(
                session,
                movie_id,
                _data.pop('genre_names'),
                False if overwrite_genres else patch,
            )
        if 'externals' in _data:
            _data['externals'] = await cls._save_externals(
                session, movie_id, _data['externals'], patch
            )
        if 'alternative_titles' in _data:
            _data['alternative_titles'] = await cls._save_alternative_titles(
                session, movie_id, _data['alternative_titles'], patch
            )
        if 'collection_name' in _data:
            collection = _data.pop('collection_name')
            if isinstance(collection, str):
                collection = await MMovieCollection.get_or_create(
                    name=collection, session=session
                )
            _data['collection_id'] = collection
        if data.rating and data.rating_votes:
            _data['rating_weighted'] = utils.calculate_weighted_rating(
                data.rating, data.rating_votes
            )
        if _data:
            await session.execute(
                sa.update(MMovie).where(MMovie.id == movie_id).values(**_data)
            )
        movie: MMovie = await session.scalar(
            sa.select(MMovie).where(MMovie.id == movie_id)
        )
        await cls._save_for_search(movie)
        return schemas.Movie.model_validate(movie)

    @staticmethod
    async def delete(movie_id: int) -> None:
        from . import MImage

        async with database.session() as session:
            async with session.begin():
                await session.execute(sa.delete(MMovie).where(MMovie.id == movie_id))
                await session.execute(
                    sa.delete(MImage).where(
                        MImage.relation_type == 'movie',
                        MImage.relation_id == movie_id,
                    )
                )
                await session.commit()
                await database.es.delete(
                    index=config.api.elasticsearch.index_prefix + 'titles',
                    id=f'movie-{movie_id}',
                )

    @staticmethod
    async def _save_externals(
        session: AsyncSession, movie_id: str | int, externals: dict[str, str], patch: bool
    ) -> dict[str, str]:
        current_externals = {}
        if not patch:
            await session.execute(
                sa.delete(Movie_external).where(Movie_external.movie_id == movie_id)
            )
        else:
            result = await session.scalars(
                sa.select(Movie_external).where(Movie_external.movie_id == movie_id)
            )
            if result:
                for external in result:
                    current_externals[external.title] = external.value

        for key in externals:
            if externals[key]:
                dup_movie = await session.scalar(
                    sa.select(MMovie).where(
                        Movie_external.title == key,
                        Movie_external.value == externals[key],
                        Movie_external.movie_id != movie_id,
                        MMovie.id == Movie_external.movie_id,
                    )
                )
                if dup_movie:
                    raise exceptions.Movie_external_duplicated(
                        external_title=key,
                        external_value=externals[key],
                        movie=utils.json_loads(
                            utils.json_dumps(schemas.Movie.model_validate(dup_movie))
                        ),
                    )

            if key not in current_externals:
                if externals[key]:
                    await session.execute(
                        sa.insert(Movie_external).values(
                            movie_id=movie_id, title=key, value=externals[key]
                        )
                    )
                    current_externals[key] = externals[key]
            elif current_externals[key] != externals[key]:
                if externals[key]:
                    await session.execute(
                        sa.update(Movie_external)
                        .where(
                            Movie_external.movie_id == movie_id,
                            Movie_external.title == key,
                        )
                        .values(value=externals[key])
                    )
                    current_externals[key] = externals[key]
                else:
                    await session.execute(
                        sa.delete(Movie_external).where(
                            Movie_external.movie_id == movie_id,
                            Movie_external.title == key,
                        )
                    )
                    current_externals.pop(key)
        return current_externals

    @staticmethod
    async def _save_alternative_titles(
        session, movie_id: str | int, alternative_titles: list[str], patch: bool
    ):
        if not patch:
            return set(alternative_titles)
        current_alternative_titles = await session.scalar(
            sa.select(MMovie.alternative_titles).where(MMovie.id == movie_id)
        )
        return set(current_alternative_titles + alternative_titles)

    @staticmethod
    async def _save_genres(
        session: AsyncSession, movie_id: str | int, genres: list[str | int], patch: bool
    ) -> list[schemas.Genre]:
        genre_ids: set[int] = await MGenre.get_or_create_genres(genres, type_='movie')
        current_genres: set[int] = set()
        if patch:
            current_genres = set(
                await session.scalars(
                    sa.select(MMovieGenre.genre_id).where(
                        MMovieGenre.movie_id == movie_id
                    )
                )
            )
        else:
            await session.execute(
                sa.delete(MMovieGenre).where(MMovieGenre.movie_id == movie_id)
            )
        new_genre_ids = genre_ids - current_genres
        if new_genre_ids:
            await session.execute(
                sa.insert(MMovieGenre).prefix_with('IGNORE'),
                [
                    {'movie_id': movie_id, 'genre_id': genre_id}
                    for genre_id in new_genre_ids
                ],
            )
        if new_genre_ids != current_genres:
            await session.execute(
                sa.text(
                    'update genres set number_of = (select count(genres.id) from movie_genres where movie_genres.genre_id = genres.id) where type="movie"'
                )
            )
        rr = await session.scalars(
            sa.select(MGenre)
            .where(MMovieGenre.movie_id == movie_id, MGenre.id == MMovieGenre.genre_id)
            .order_by(MGenre.name)
        )
        return [schemas.Genre.model_validate(r) for r in rr]

    @staticmethod
    async def _save_for_search(movie: MMovie) -> None:
        doc = movie.title_document()
        if not doc:
            return
        await database.es.index(
            index=config.api.elasticsearch.index_prefix + 'titles',
            id=f'movie-{movie.id}',
            document=doc.model_dump(),
        )

    def title_document(self) -> schemas.Search_title_document:
        if not self.title:
            return None
        titles = [self.title, *self.alternative_titles]
        year = str(self.release_date.year) if self.release_date else ''
        for title in titles[:]:
            if title and year not in title:
                t = f'{title} {year}'
                if t not in titles:
                    titles.append(t)
        return schemas.Search_title_document(
            type='movie',
            id=self.id,
            title=self.title,
            titles=[schemas.Search_title_document_title(title=title) for title in titles],
            release_date=self.release_date,
            imdb=self.externals.get('imdb'),
            poster_image=schemas.Image.model_validate(self.poster_image)
            if self.poster_image
            else None,
            popularity=self.popularity or 0,
            genres=self.genres,
            rating=self.rating,
            rating_votes=self.rating_votes,
            runtime=self.runtime,
            language=self.language,
        )

    @staticmethod
    @auto_session
    async def get_from_external(
        title: str,
        value: str,
        session: AsyncSession = None,
    ):
        movie = await session.scalar(
            sa.select(MMovie).where(
                MMovie.id == Movie_external.movie_id,
                Movie_external.title == title,
                Movie_external.value == value,
            )
        )
        if movie:
            return schemas.Movie.model_validate(movie)
        return None


class Movie_external(Base):
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

    @staticmethod
    @auto_session
    async def increment(
        user_id: int | str,
        movie_id: int,
        data: schemas.Movie_watched_increment,
        session: AsyncSession = None,
    ):
        watched = sa.dialects.mysql.insert(MMovieWatched).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=data.watched_at.astimezone(UTC),
            times=1,
        )
        watched = watched.on_duplicate_key_update(
            watched_at=watched.inserted.watched_at,
            times=MMovieWatched.times + 1,
            position=0,
        )
        watched_history = sa.insert(MMovieWatchedHistory).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=data.watched_at.astimezone(UTC),
        )

        await session.execute(watched)
        await session.execute(watched_history)
        await session.execute(
            sa.delete(MMovieWatchlist).where(
                MMovieWatchlist.user_id == user_id,
                MMovieWatchlist.movie_id == movie_id,
            )
        )
        w = await session.scalar(
            sa.select(MMovieWatched).where(
                MMovieWatched.movie_id == movie_id,
                MMovieWatched.user_id == user_id,
            )
        )
        return schemas.Movie_watched.model_validate(w)

    @staticmethod
    @auto_session
    async def decrement(user_id: int | str, movie_id: int, session: AsyncSession = None):
        w = await session.scalar(
            sa.select(MMovieWatched).where(
                MMovieWatched.movie_id == movie_id,
                MMovieWatched.user_id == user_id,
            )
        )
        if not w:
            return None

        if w.times == 0 or (w.times == 1 and w.position == 0):
            await session.execute(
                sa.delete(MMovieWatched).where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
            )
            await session.execute(
                sa.delete(MMovieWatchedHistory).where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
            )
            return None
        if w.position > 0:
            watched_at = await session.scalar(
                sa.select(MMovieWatchedHistory.watched_at)
                .where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
                .order_by(MMovieWatchedHistory.watched_at.desc())
                .limit(1)
            )
            await session.execute(
                sa.update(MMovieWatched)
                .where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
                .values(
                    position=0,
                    watched_at=watched_at,
                )
            )
        else:
            e = await session.execute(
                sa.select(MMovieWatchedHistory.id, MMovieWatchedHistory.watched_at)
                .where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
                .order_by(MMovieWatchedHistory.watched_at.desc())
                .limit(2)
            )
            e = e.all()
            await session.execute(
                sa.delete(MMovieWatchedHistory).where(
                    MMovieWatchedHistory.id == e[0].id,
                )
            )
            await session.execute(
                sa.update(MMovieWatched)
                .where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
                .values(
                    times=MMovieWatched.times - 1,
                    position=0,
                    watched_at=e[1].watched_at,
                )
            )

        w = await session.scalar(
            sa.select(MMovieWatched).where(
                MMovieWatched.movie_id == movie_id,
                MMovieWatched.user_id == user_id,
            )
        )
        if w:
            return schemas.Movie_watched.model_validate(w)
        return None

    @staticmethod
    @auto_session
    async def set_position(
        user_id: int | str, movie_id: int, position: int, session: AsyncSession = None
    ) -> None:
        if position == 0:
            await MMovieWatched.reset_position(user_id=user_id, movie_id=movie_id)
            return
        sql = sa.dialects.mysql.insert(MMovieWatched).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=datetime.now(tz=UTC),
            position=position,
        )
        sql = sql.on_duplicate_key_update(
            watched_at=sql.inserted.watched_at,
            position=sql.inserted.position,
        )
        await session.execute(sql)

    @staticmethod
    @auto_session
    async def reset_position(
        user_id: int | str, movie_id: int, session: AsyncSession = None
    ) -> None:
        w = await session.scalar(
            sa.select(MMovieWatched).where(
                MMovieWatched.movie_id == movie_id,
                MMovieWatched.user_id == user_id,
            )
        )
        if not w:
            return
        if w.times < 1:
            await session.execute(
                sa.delete(MMovieWatched).where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
            )
            await session.execute(
                sa.delete(MMovieWatchedHistory).where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
            )
            return
        if w.position > 0:
            watched_at = await session.scalar(
                sa.select(MMovieWatchedHistory.watched_at)
                .where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
                .order_by(MMovieWatchedHistory.watched_at.desc())
                .limit(1)
            )
            await session.execute(
                sa.update(MMovieWatched)
                .where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
                .values(
                    position=0,
                    watched_at=watched_at,
                )
            )
        else:
            return


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


async def rebuild_movies() -> None:
    async def c():
        async with database.session() as session:
            result = await session.stream(sa.select(MMovie))
            async for movies in result.yield_per(1000):
                for movie in movies:
                    d = movie.title_document()
                    if not d:
                        continue
                    yield {
                        '_index': config.api.elasticsearch.index_prefix + 'titles',
                        '_id': f'movie-{movie.id}',
                        **d.model_dump(),
                    }

    from elasticsearch import helpers

    await helpers.async_bulk(database.es, c())
