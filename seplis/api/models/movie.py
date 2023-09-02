import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from seplis import utils
from seplis.utils.sqlalchemy import UtcDateTime
from .genre import Genre
from .movie_collection import Movie_collection
from .movie_watchlist import Movie_watchlist
from .base import Base
from ..database import auto_session, database
from .. import schemas, exceptions
from ... import config


class Movie(Base):
    __tablename__ = 'movies'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    title = sa.Column(sa.String(200))
    original_title = sa.Column(sa.String(200))
    alternative_titles = sa.Column(sa.JSON, nullable=False)
    externals = sa.Column(sa.JSON, nullable=False)
    created_at = sa.Column(UtcDateTime)
    updated_at = sa.Column(UtcDateTime)
    status = sa.Column(sa.SmallInteger)
    plot = sa.Column(sa.String(2000), nullable=True)
    tagline = sa.Column(sa.String(500), nullable=True)
    language = sa.Column(sa.String(20), nullable=True)
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    poster_image = sa.orm.relationship('Image', lazy=False)
    runtime = sa.Column(sa.Integer, nullable=True)
    release_date = sa.Column(sa.Date, nullable=True)
    budget = sa.Column(sa.BIGINT, nullable=True)
    revenue = sa.Column(sa.BIGINT, nullable=True)
    genres = sa.Column(sa.JSON(), default=lambda: [])
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4), nullable=True)
    rating = sa.Column(sa.DECIMAL(4, 2), nullable=True)
    rating_votes = sa.Column(sa.Integer, nullable=True)
    rating_weighted = sa.Column(sa.Float(), nullable=False, server_default='0')
    collection_id = sa.Column(sa.Integer, sa.ForeignKey('movie_collections.id'), nullable=True)
    collection = sa.orm.relationship('Movie_collection', lazy=False)

    @classmethod
    @auto_session
    async def save(cls, 
        data: schemas.Movie_create | schemas.Movie_update, 
        movie_id: int | None = None, 
        patch = True,
        overwrite_genres = False,
        session = None,
    ):
        _data = data.model_dump(exclude_unset=True) if data else {}
        if not movie_id:
            r = await session.execute(sa.insert(Movie))
            movie_id = r.lastrowid
            _data['created_at'] = datetime.now(tz=timezone.utc)
        else:
            m = await session.scalar(sa.select(Movie.id).where(Movie.id == movie_id))
            if not m:
                raise HTTPException(404, f'Unknown movie id: {movie_id}')
            _data['updated_at'] = datetime.now(tz=timezone.utc)
        if 'genre_names' in _data:
            _data['genres'] = await cls._save_genres(session, movie_id, _data.pop('genre_names'), False if overwrite_genres else patch)
        if 'externals' in _data:
            _data['externals'] = await cls._save_externals(session, movie_id, _data['externals'], patch)
        if 'alternative_titles' in _data:
            _data['alternative_titles'] = await cls._save_alternative_titles(session, movie_id, _data['alternative_titles'], patch)
        if 'collection_name' in _data:
            collection = _data.pop('collection_name')
            if isinstance(collection, str):
                collection = await Movie_collection.get_or_create(name=collection, session=session)
            _data['collection_id'] = collection
        if data.rating and data.rating_votes:
            _data['rating_weighted'] = utils.calculate_weighted_rating(data.rating, data.rating_votes)
        if _data:
            await session.execute(sa.update(Movie).where(Movie.id == movie_id).values(**_data))
        movie: Movie = await session.scalar(sa.select(Movie).where(Movie.id == movie_id))
        await cls._save_for_search(movie)
        return schemas.Movie.model_validate(movie)

    @staticmethod
    async def delete(movie_id: int):
        from . import Image
        async with database.session() as session:
            async with session.begin():
                await session.execute(sa.delete(Movie).where(
                    Movie.id == movie_id)
                )
                await session.execute(sa.delete(Image).where(
                    Image.relation_type == 'movie',
                    Image.relation_id == movie_id,
                ))
                await session.commit()
                await database.es.delete(
                    index=config.data.api.elasticsearch.index_prefix+'titles',
                    id=f'movie-{movie_id}',
                )

    @staticmethod
    async def _save_externals(session: AsyncSession, movie_id: str | int, externals: dict[str, str], patch: bool) -> dict[str, str]:
        current_externals = {}
        if not patch:
            await session.execute(sa.delete(Movie_external).where(Movie_external.movie_id == movie_id))
        else:
            result = await session.scalars(sa.select(Movie_external).where(Movie_external.movie_id == movie_id))
            if result:
                for external in result:
                    current_externals[external.title] = external.value

        for key in externals:
            if externals[key]:
                dup_movie = await session.scalar(sa.select(Movie).where(
                    Movie_external.title == key,
                    Movie_external.value == externals[key],
                    Movie_external.movie_id != movie_id,
                    Movie.id == Movie_external.movie_id,
                ))
                if dup_movie:
                    raise exceptions.Movie_external_duplicated(
                        external_title=key,
                        external_value=externals[key],
                        movie=utils.json_loads(utils.json_dumps(
                            schemas.Movie.model_validate(dup_movie)))
                    )

            if (key not in current_externals):
                if externals[key]:
                    await session.execute(sa.insert(Movie_external)
                                          .values(movie_id=movie_id, title=key, value=externals[key]))
                    current_externals[key] = externals[key]
            elif (current_externals[key] != externals[key]):
                if (externals[key]):
                    await session.execute(sa.update(Movie_external).where(
                        Movie_external.movie_id == movie_id,
                        Movie_external.title == key,
                    ).values(value=externals[key]))
                    current_externals[key] = externals[key]
                else:
                    await session.execute(sa.delete(Movie_external).where(
                        Movie_external.movie_id == movie_id,
                        Movie_external.title == key
                    ))
                    current_externals.pop(key)
        return current_externals

    @staticmethod
    async def _save_alternative_titles(session, movie_id: str | int, alternative_titles: list[str], patch: bool):
        if not patch:
            return set(alternative_titles)
        current_alternative_titles = await session.scalar(sa.select(Movie.alternative_titles).where(Movie.id == movie_id))
        return set(current_alternative_titles + alternative_titles)

    @staticmethod
    async def _save_genres(session: AsyncSession, movie_id: str | int, genres: list[str | int], patch: bool) -> list[schemas.Genre]:
        genre_ids: set[int] = await Genre.get_or_create_genres(genres, type_='movie')
        current_genres: set[int] = set()
        if patch:
            current_genres = set(await session.scalars(sa.select(Movie_genre.genre_id).where(Movie_genre.movie_id == movie_id)))
        else:
            await session.execute(sa.delete(Movie_genre).where(Movie_genre.movie_id == movie_id))
        new_genre_ids = (genre_ids - current_genres)
        if new_genre_ids:
            await session.execute(sa.insert(Movie_genre).prefix_with('IGNORE'), [
                {'movie_id': movie_id, 'genre_id': genre_id} for genre_id in new_genre_ids
            ])
        if new_genre_ids != current_genres:            
            await session.execute(sa.text('update genres set number_of = (select count(genres.id) from series_genres where series_genres.genre_id = genres.id)' ))
        rr = await session.scalars(sa.select(Genre).where(Movie_genre.movie_id == movie_id, Genre.id == Movie_genre.genre_id).order_by(Genre.name))
        return [schemas.Genre.model_validate(r) for r in rr]

    @staticmethod
    async def _save_for_search(movie: 'Movie'):
        doc = movie.title_document()
        if not doc:
            return
        await database.es.index(
            index=config.data.api.elasticsearch.index_prefix+'titles',
            id=f'movie-{movie.id}',
            document=doc.model_dump(),
        )

    def title_document(self) -> schemas.Search_title_document:
        if not self.title:
            return
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
            poster_image=schemas.Image.model_validate(
                self.poster_image) if self.poster_image else None,
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
        movie = await session.scalar(sa.select(Movie).where(
            Movie.id == Movie_external.movie_id,
            Movie_external.title == title,
            Movie_external.value == value,
        ))
        if movie:
            return schemas.Movie.model_validate(movie)


class Movie_external(Base):
    __tablename__ = 'movie_externals'

    movie_id = sa.Column(sa.Integer, sa.ForeignKey(
        'movies.id'), primary_key=True, autoincrement=False)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))


class Movie_watched(Base):
    __tablename__ = 'movies_watched'
    __serialize_ignore__ = ('movie_id', 'user_id',)

    movie_id = sa.Column(sa.Integer, sa.ForeignKey(
        'movies.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(
        'users.id'), primary_key=True, autoincrement=False)
    times = sa.Column(sa.SmallInteger)
    position = sa.Column(sa.SmallInteger)
    watched_at = sa.Column(UtcDateTime, nullable=False)

    @staticmethod
    @auto_session
    async def increment(user_id: int | str, movie_id: int, data: schemas.Movie_watched_increment, session: AsyncSession = None):
        watched = sa.dialects.mysql.insert(Movie_watched).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=data.watched_at.astimezone(timezone.utc),
            times=1
        )
        watched = watched.on_duplicate_key_update(
            watched_at=watched.inserted.watched_at,
            times=Movie_watched.times + 1,
            position=0,
        )
        watched_history = sa.insert(Movie_watched_history).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=data.watched_at.astimezone(timezone.utc),
        )

        await session.execute(watched)
        await session.execute(watched_history)
        await session.execute(sa.delete(Movie_watchlist).where(
            Movie_watchlist.user_id == user_id,
            Movie_watchlist.movie_id == movie_id,
        ))
        w = await session.scalar(sa.select(Movie_watched).where(
            Movie_watched.movie_id == movie_id,
            Movie_watched.user_id == user_id,
        ))
        return schemas.Movie_watched.model_validate(w)


    @staticmethod
    @auto_session
    async def decrement(user_id: int | str, movie_id: int, session: AsyncSession = None):
        w = await session.scalar(sa.select(Movie_watched).where(
            Movie_watched.movie_id == movie_id,
            Movie_watched.user_id == user_id,
        ))
        if not w:
            return
      
        if w.times == 0 or (w.times == 1 and w.position == 0):
            await session.execute(sa.delete(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ))
            await session.execute(sa.delete(Movie_watched_history).where(
                Movie_watched_history.movie_id == movie_id,
                Movie_watched_history.user_id == user_id,
            ))
            return
        elif w.position > 0:
            watched_at = await session.scalar(sa.select(Movie_watched_history.watched_at).where(
                Movie_watched_history.movie_id == movie_id,
                Movie_watched_history.user_id == user_id,
            ).order_by(
                Movie_watched_history.watched_at.desc()
            ).limit(1))
            await session.execute(sa.update(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ).values(
                position=0,
                watched_at=watched_at,
            ))
        else:
            e = await session.execute(sa.select(Movie_watched_history.id, Movie_watched_history.watched_at).where(
                Movie_watched_history.movie_id == movie_id,
                Movie_watched_history.user_id == user_id,
            ).order_by(
                Movie_watched_history.watched_at.desc()
            ).limit(2))
            e = e.all()
            await session.execute(sa.delete(Movie_watched_history).where(
                Movie_watched_history.id == e[0].id,
            ))
            await session.execute(sa.update(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ).values(
                times=Movie_watched.times - 1,
                position=0,
                watched_at=e[1].watched_at,
            ))

        w = await session.scalar(sa.select(Movie_watched).where(
            Movie_watched.movie_id == movie_id,
            Movie_watched.user_id == user_id,
        ))
        if w:
            return schemas.Movie_watched.model_validate(w)


    @staticmethod
    @auto_session
    async def set_position(user_id: int | str, movie_id: int, position: int, session: AsyncSession = None):
        if position == 0:
            await Movie_watched.reset_position(user_id=user_id, movie_id=movie_id)
            return
        sql = sa.dialects.mysql.insert(Movie_watched).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=datetime.now(tz=timezone.utc),
            position=position,
        )
        sql = sql.on_duplicate_key_update(
            watched_at=sql.inserted.watched_at,
            position=sql.inserted.position,
        )
        await session.execute(sql)


    @staticmethod
    @auto_session
    async def reset_position(user_id: int | str, movie_id: int, session: AsyncSession = None):
        w = await session.scalar(sa.select(Movie_watched).where(
            Movie_watched.movie_id == movie_id,
            Movie_watched.user_id == user_id,
        ))
        if not w:
            return
        if w.times < 1:
            await session.execute(sa.delete(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ))
            await session.execute(sa.delete(Movie_watched_history).where(
                Movie_watched_history.movie_id == movie_id,
                Movie_watched_history.user_id == user_id,
            ))
            return
        else:
            if w.position > 0:
                watched_at = await session.scalar(sa.select(Movie_watched_history.watched_at).where(
                    Movie_watched_history.movie_id == movie_id,
                    Movie_watched_history.user_id == user_id,
                ).order_by(
                    Movie_watched_history.watched_at.desc()
                ).limit(1))
                await session.execute(sa.update(Movie_watched).where(
                    Movie_watched.movie_id == movie_id,
                    Movie_watched.user_id == user_id,
                ).values(
                    position=0,
                    watched_at=watched_at,
                ))
            else:
                return


class Movie_watched_history(Base):
    __tablename__ = 'movies_watched_history'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    watched_at = sa.Column(UtcDateTime)



class Movie_genre(Base):
    __tablename__ = 'movie_genres'

    movie_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey(
        'genres.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False)


async def rebuild_movies():
    async def c():
        async with database.session() as session:
            result = await session.stream(sa.select(Movie))
            async for movies in result.yield_per(1000):
                for movie in movies:
                    d = movie.title_document()
                    if not d:
                        continue
                    yield {
                        '_index': config.data.api.elasticsearch.index_prefix+'titles',
                        '_id': f'movie-{movie.id}',
                        **d.model_dump()
                    }
    from elasticsearch import helpers
    await helpers.async_bulk(database.es, c())
