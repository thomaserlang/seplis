import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from seplis.utils.sqlalchemy import UtcDateTime
from .genre import Genre
from .base import Base
from ..database import database
from .. import schemas, rebuild_cache, exceptions
from ... import config, logger

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
    plot = sa.Column(sa.String(2000))
    tagline = sa.Column(sa.String(500))
    language = sa.Column(sa.String(20))
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    poster_image = sa.orm.relationship('Image', lazy=False)
    runtime = sa.Column(sa.Integer)
    release_date = sa.Column(sa.Date)
    budget = sa.Column(sa.Integer)
    revenue = sa.Column(sa.Integer)
    genres = sa.Column(sa.JSON(), default=lambda: [])
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4))
    rating = sa.Column(sa.DECIMAL(4, 2))


    @classmethod
    async def save(cls, data: schemas.Movie_create | schemas.Movie_update, movie_id: int | None = None, patch: bool = True) -> schemas.Movie:
        async with database.session() as session:
            async with session.begin():
                _data = data.dict(exclude_unset=True)
                if not movie_id:
                    r = await session.execute(sa.insert(Movie))
                    movie_id = r.lastrowid
                    _data['created_at'] = datetime.now(tz=timezone.utc)
                else:
                    m = await session.scalar(sa.select(Movie.id).where(Movie.id == movie_id))
                    if not m:
                        raise HTTPException(404, f'Unknown movie id: {movie_id}')
                    _data['updated_at'] = datetime.now(tz=timezone.utc)
                if 'genres' in _data:
                    _data['genres'] = await cls._save_genres(session, movie_id, _data['genres'], patch)
                if 'externals' in _data:
                    _data['externals'] = await cls._save_externals(session, movie_id, _data['externals'], patch)
                if 'alternative_titles' in _data:
                    _data['alternative_titles'] = await cls._save_alternative_titles(session, movie_id, _data['alternative_titles'], patch)
                if _data:
                    await session.execute(sa.update(Movie).where(Movie.id == movie_id).values(**_data))
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
                        movie=schemas.Movie.from_orm(dup_movie)
                    )
                    
            if (key not in current_externals):
                if externals[key]:
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
    async def _save_genres(session: AsyncSession, movie_id: str | int, genres: list[str | int], patch: bool) -> list[schemas.Genre]:
        genre_ids = await Genre.get_or_create_genres(session, genres)
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
        rr = await session.scalars(sa.select(Genre).where(Movie_genre.movie_id == movie_id, Genre.id == Movie_genre.genre_id).order_by(Genre.name))
        return [schemas.Genre.from_orm(r) for r in rr]


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


def movie_user_query(user_id: int, sort: schemas.MOVIE_USER_SORT_TYPE | None, filter_query: schemas.Movie_user_query_filter | None):
    query = sa.select(
        Movie,        
        sa.func.IF(Movie_stared.user_id != None, 1, 0).label('stared'),
        Movie_watched,
    ).join(
        Movie_stared, sa.and_(
            Movie_stared.user_id == user_id,
            Movie_stared.movie_id == Movie.id,
        ),
        isouter=True,
    ).join(
        Movie_watched, sa.and_(
            Movie_watched.user_id == user_id,
            Movie_watched.movie_id == Movie.id,
        ),
        isouter=True,
    )

    if filter_query:
        if filter_query.genre_id:
            if len(filter_query.genre_id) == 1:
                query = query.where(
                    Movie_genre.genre_id == filter_query.genre_id[0],
                    Movie.id == Movie_genre.movie_id,
                )
            else:                
                query = query.where(
                    Movie_genre.genre_id.in_(filter_query.genre_id),
                    Movie.id == Movie_genre.movie_id,
                )

    if sort == 'stared_at_desc':
        query = query.order_by(
            sa.desc(sa.func.coalesce(Movie_stared.created_at, -1)),
            sa.desc(Movie.id),
        )
    elif sort == 'stared_at_asc':
        query = query.order_by(
            sa.asc(sa.func.coalesce(Movie_stared.created_at, -1)),
            sa.asc(Movie.id),
        )
    elif sort == 'watched_at_desc':
        query = query.order_by(
            sa.desc(sa.func.coalesce(Movie_watched.watched_at, -1)),
            sa.desc(Movie.id),
        )
    elif sort == 'watched_at_asc':
        query = query.order_by(
            sa.asc(sa.func.coalesce(Movie_watched.watched_at, -1)),
            sa.asc(Movie.id),
        )
    elif sort == 'rating_desc':
        query = query.order_by(
            sa.desc(sa.func.coalesce(Movie.rating, -1)),
            sa.desc(Movie.id),
        )
    elif sort == 'rating_asc':
        query = query.order_by(
            sa.asc(sa.func.coalesce(Movie.rating, -1)),
            sa.asc(Movie.id),
        )
    elif sort == 'popularity_desc':
        query = query.order_by(
            sa.desc(sa.func.coalesce(Movie.popularity, -1)),
            sa.desc(Movie.id),
        )
    elif sort == 'popularity_asc':
        query = query.order_by(
            sa.asc(sa.func.coalesce(Movie.popularity, -1)),
            sa.asc(Movie.id),
        )

    return query

def movie_user_result_parse(row: any):
    return schemas.Movie_user(
        movie=schemas.Movie.from_orm(row.Movie),
        stared=row.stared == 1,
        watched_data=schemas.Movie_watched.from_orm(row.Movie_watched),
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
    watched_at = sa.Column(UtcDateTime, nullable=False)


    @staticmethod
    async def increment(user_id: int | str, movie_id: int, data: schemas.Movie_watched_increment) -> schemas.Movie_watched:
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
    async def decrement(user_id: int | str, movie_id: int) -> schemas.Movie_watched | None:
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


    @staticmethod
    async def set_position(user_id: int | str, movie_id: int, position: int):
        if position == 0:
            await Movie_watched.reset_position(user_id=user_id, movie_id=movie_id)
            return
        async with database.session() as session:
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
            await session.commit()


    @staticmethod
    async def reset_position(user_id: int | str, movie_id: int):
        async with database.session() as session:
            w = await session.scalar(sa.select(Movie_watched).where(
                Movie_watched.movie_id == movie_id,
                Movie_watched.user_id == user_id,
            ))
            if not w:
                return
            if w.times < 1:
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
                    await session.commit()
                else:
                    return


class Movie_watched_history(Base):
    __tablename__ = 'movies_watched_history'
    
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    watched_at = sa.Column(UtcDateTime)


class Movie_stared(Base):
    __tablename__ = 'movies_stared'
    
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(UtcDateTime, nullable=False)

    @staticmethod
    async def set_stared(user_id: int | str, movie_id: int):
        async with database.session() as session:
            await session.execute(sa.insert(Movie_stared).values(
                movie_id=movie_id,
                user_id=user_id,
                created_at=datetime.now(tz=timezone.utc),
            ).prefix_with('IGNORE'))
            await session.commit()

    @staticmethod
    async def remove_stared(user_id: int | str, movie_id: int):
        async with database.session() as session:
            await session.execute(sa.delete(Movie_stared).where(
                Movie_stared.movie_id == movie_id,
                Movie_stared.user_id == user_id,
            ))
            await session.commit()


class Movie_genre(Base):
    __tablename__ = 'movie_genres'

    movie_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey('genres.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False)


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