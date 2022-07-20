from __future__ import annotations
from ast import Dict
from typing import List, Union
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from seplis.api import rebuild_cache
from seplis.api.decorators import new_session
from seplis.api.schemas import Movie_schema
from .base import Base
from seplis.api.connections import database
from elasticsearch import helpers


class Movie(Base):
    __tablename__ = 'movies'
    __serialize_ignore__ = ('poster_image_id',)

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
    async def save(cls, session: AsyncSession, movie: Movie_schema, movie_id: Union[int, str, None] = None, patch: bool = False) -> Movie:
        data = movie.dict(exclude_unset=True)
        if not movie_id:
            r = await session.execute(sa.insert(cls))
            movie_id = r.lastrowid
        if 'externals' in data:
            data['externals'] = await cls._save_externals(session, movie_id, data['externals'], patch)
        if 'alternative_titles' in data:
            data['alternative_titles'] = await cls._save_alternative_titles(session, movie_id, data['alternative_titles'], patch)
        await session.execute(sa.update(cls).where(cls.id == movie_id).values(**data))
        r = await session.scalars(sa.select(cls).where(cls.id == movie_id))
        movie = r.one()
        await cls._save_for_search(movie)
        return movie

    @staticmethod
    async def _save_externals(session, movie_id: str, externals: Dict[str, str], patch: bool) -> Dict[str, str]:
        current_externals = {}
        if not patch:
            await session.execute(sa.delete(Movie_external).where(Movie_external.movie_id == movie_id))
        else:
            current_externals = await session.scalar(sa.select(Movie.externals).where(Movie.id == movie_id))
        for key in externals:
            if (key not in current_externals):
                await session.execute(sa.insert(Movie_external)\
                    .values(movie_id=movie_id, title=key, value=externals[key]))
            elif (current_externals[key] != externals[key]):
                await session.execute(sa.update(Movie_external).where(
                    Movie_external.movie_id == movie_id,
                    Movie_external.title == key,
                ).values(value=externals[key]))
        current_externals.update(externals)
        return current_externals

    @staticmethod
    async def _save_alternative_titles(session, movie_id: str, alternative_titles: List[str], patch: bool):
        if not patch:
            return set(alternative_titles)
        current_alternative_titles = await session.scalar(sa.select(Movie.alternative_titles).where(Movie.id == movie_id))
        return set(current_alternative_titles + alternative_titles)
    
    @staticmethod
    async def _save_for_search(movie: Movie):
        await database.es_async.index(
            index='titles',
            id=f'movie-{movie.id}',
            document=movie.title_document(),
        )

    def title_document(self):
        at = [self.title, *self.alternative_titles]
        year = str(self.release_date.year) if self.release_date else ''
        for title in at[:]:
            if title and year not in title:
                t = f'{title} {year}'
                if t not in at:
                    at.append(t)
        return {
            'type': 'movie',
            'id': self.id,
            'title': self.title,
            'titles': at,
            'release_date': self.release_date,
            'imdb': self.externals.get('imdb'),
            'poster_image': self.poster_image.serialize() if self.poster_image else None,
        }

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
    helpers.bulk(database.es, c())