import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timezone

from .base import Base
from ..database import database
from .. import schemas, rebuild_cache
from ... import config, logger

class Movie(Base):
    __tablename__ = 'movies'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    title = sa.Column(sa.String(200))
    alternative_titles = sa.Column(sa.JSON, nullable=False)
    externals = sa.Column(sa.JSON, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = sa.Column(sa.SmallInteger)
    description = sa.Column(sa.String(2000))
    language = sa.Column(sa.String(20))
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    poster_image = sa.orm.relationship('Image', lazy=False)
    runtime = sa.Column(sa.Integer)
    release_date = sa.Column(sa.Date)

    @classmethod
    async def save(cls, movie_data: schemas.Movie_create | schemas.Movie_update, movie_id: int | str | None = None, patch: bool = False) -> schemas.Movie:
        async with database.session() as session:
            async with session.begin():
                data = movie_data.dict(exclude_unset=True)
                if not movie_id:
                    r = await session.execute(sa.insert(Movie))
                    movie_id = r.lastrowid
                else:
                    m = await session.scalar(sa.select(Movie.id).where(Movie.id == movie_id))
                    if not m:
                        raise HTTPException(404, f'Unknown movie id: {movie_id}')
                if 'externals' in data:
                    data['externals'] = await cls._save_externals(session, movie_id, data['externals'], patch)
                if 'alternative_titles' in data:
                    data['alternative_titles'] = await cls._save_alternative_titles(session, movie_id, data['alternative_titles'], patch)
                await session.execute(sa.update(Movie).where(Movie.id == movie_id).values(**data))
                movie: Movie = await session.scalar(sa.select(Movie).where(Movie.id == movie_id))
                await session.commit()
                await cls._save_for_search(movie)
                return schemas.Movie.from_orm(movie)

    @classmethod
    async def delete(self, movie_id: int):    
        from . import Image
        async with database.session() as session:
            async with session.begin():
                await asyncio.gather(
                    session.execute(sa.delete(Movie).where(Movie.id == movie_id)),
                    session.execute(sa.delete(Image).where(
                        Image.relation_type == 'movie',
                        Image.relation_id == movie_id,
                    )),
                )
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
            current_externals = await session.scalar(sa.select(Movie.externals).where(Movie.id == movie_id))

        for key in externals:
            if externals[key]:
                r = await session.scalar(sa.select(Movie_external.movie_id).where(
                    Movie_external.title == key,
                    Movie_external.value == externals[key],
                    Movie_external.movie_id != movie_id,
                ))
                if r:
                    raise HTTPException(400, f'Movie with {key}={externals[key]} already exists (Movie id: {r}).')
            if (key not in current_externals):
                await session.execute(sa.insert(Movie_external)\
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
    async def _save_for_search(movie: 'Movie'):
        doc = movie.title_document()
        if not doc:
            return
        await database.es.index(
            index=config.data.api.elasticsearch.index_prefix+'titles',
            id=f'movie-{movie.id}',
            document=doc.dict(),
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
            type = 'movie',
            id = self.id,
            title = self.title,
            titles = [{'title': title} for title in titles],
            release_date = self.release_date,
            imdb = self.externals.get('imdb'),
            poster_image = schemas.Image.from_orm(self.poster_image) if self.poster_image else None,
        )


class Movie_external(Base):
    __tablename__ = 'movie_externals'

    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))


class Movie_watched(Base):
    __tablename__ = 'movies_watched'
    __serialize_ignore__ = ('movie_id', 'user_id',)

    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    times = sa.Column(sa.SmallInteger)
    position = sa.Column(sa.SmallInteger)
    watched_at = sa.Column(sa.DateTime)


    @staticmethod
    async def increment(user_id: int, movie_id: int, data: schemas.Movie_watched_increment) -> schemas.Movie_watched:
        async with database.session() as session:
            sql = sa.dialects.mysql.insert(Movie_watched).values(
                movie_id=movie_id,
                user_id=user_id,
                watched_at=data.watched_at.astimezone(timezone.utc),
                times=1
            )
            sql = sql.on_duplicate_key_update(
                watched_at=sql.inserted.watched_at,
                times=Movie_watched.times + 1,
                position=0,
            )
            sql_history = sa.insert(Movie_watched_history).values(
                movie_id=movie_id,
                user_id=user_id,
                watched_at=data.watched_at.astimezone(timezone.utc),
            )
            await asyncio.gather(
                session.execute(sql),
                session.execute(sql_history),
            )
            w = await session.scalar(sa.select(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ))
            await session.commit()
            return schemas.Movie_watched.from_orm(w)


    @staticmethod
    async def decrement(user_id: int, movie_id: int) -> schemas.Movie_watched | None:
        async with database.session() as session:
            w = await session.scalar(sa.select(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ))
            if not w:
                return
            if w.times <= 1:
                await asyncio.gather(
                    session.execute(sa.delete(Movie_watched).where(
                        Movie_watched.movie_id == movie_id,
                        Movie_watched.user_id == user_id,
                    )),
                    session.execute(sa.delete(Movie_watched_history).where(
                        Movie_watched_history.movie_id == movie_id,
                        Movie_watched_history.user_id == user_id,
                    )),
                )
                await session.commit()
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
                    id_ = await session.scalar(sa.select(Movie_watched_history.id).where(
                        Movie_watched_history.movie_id == movie_id,
                        Movie_watched_history.user_id == user_id,
                    ).order_by(
                        Movie_watched_history.watched_at.desc()
                    ).limit(1))
                    await session.execute(sa.delete(Movie_watched_history).where(
                        Movie_watched_history.id == id_,
                    ))
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
                        times=Movie_watched.times - 1,
                        position=0,
                        watched_at=watched_at,
                    ))
                    
            w = await session.scalar(sa.select(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ))
            await session.commit()
            return schemas.Movie_watched.from_orm(w)


class Movie_watched_history(Base):
    __tablename__ = 'movies_watched_history'
    
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    watched_at = sa.Column(sa.DateTime)


class Movie_stared(Base):
    __tablename__ = 'movies_stared'
    
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(sa.DateTime)


@rebuild_cache.register('movies')
def rebuild_movies():
    def c():
        with new_session() as session:
            for item in session.query(Movie).yield_per(10000):
                yield {
                    '_index': 'titles',
                    '_id': f'movie-{item.id}',
                    **item.title_document()
                }
    from elasticsearch import helpers
    helpers.async_bulk(database.es, c())