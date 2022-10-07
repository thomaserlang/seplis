import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generator
from .episode import Episode
from .base import Base

from ..database import database
from .. import schemas, rebuild_cache
from ... import config, logger, utils, constants

class Series(Base):
    __tablename__ = 'shows'
    __serialize_ignore__ = ('description_text', 'description_title', 'description_url',
                            'importer_info', 'importer_episodes', 'poster_image_id')

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, onupdate=datetime.utcnow)
    status = sa.Column(sa.Integer, default=0, nullable=False)
    fans = sa.Column(sa.Integer, default=0)
    title = sa.Column(sa.String(200))
    description_text = sa.Column(sa.Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    premiered = sa.Column(sa.Date)
    ended = sa.Column(sa.Date)
    externals = sa.Column(sa.JSON(), default=lambda: {})
    importer_info = sa.Column(sa.String(45))
    importer_episodes = sa.Column(sa.String(45))
    seasons = sa.Column(sa.JSON(), default=lambda: [])
    runtime = sa.Column(sa.Integer)
    genres = sa.Column(sa.JSON(), default=lambda: [])
    alternative_titles = sa.Column(sa.JSON(), default=lambda: [])
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    poster_image = sa.orm.relationship('Image', lazy=False)
    episode_type = sa.Column(
        sa.Integer, 
        default=constants.SHOW_EPISODE_TYPE_SEASON_EPISODE,
    )
    total_episodes = sa.Column(sa.Integer, default=0)
    language = sa.Column(sa.String(100))

    @property
    def description(self):
        return {
            'text': self.description_text,
            'title': self.description_title,
            'url': self.description_url,
        }

    @property
    def importers(self):
        return {
            'info': self.importer_info,
            'episodes': self.importer_episodes,
        }
 
    @classmethod
    async def save(cls, series: schemas.Series_create | schemas.Series_update, series_id: int | str | None, patch=False) -> schemas.Series:
        data = series.dict(exclude_unset=True)
        async with database.session() as session:
            async with session.begin():
                if not series_id:
                    r = await session.execute(sa.insert(Series))
                    series_id = r.lastrowid
                else:
                    m = await session.scalar(sa.select(Series.id).where(Series.id == series_id))
                    if not m:
                        raise HTTPException(404, f'Unknown series id: {series_id}')
                if 'externals' in data:
                    data['externals'] = await cls._save_externals(session, series_id, data['externals'], patch)
                if 'alternative_titles' in data:
                    data['alternative_titles'] = await cls._save_alternative_titles(session, series_id, data['alternative_titles'], patch)
                if 'genres' in data:
                    data['genres'] = await cls._save_genres(session, series_id, data['genres'], patch)
                if 'importers' in data:
                    data.update(utils.flatten(data.pop('importers'), 'importer'))
                if 'description' in data:
                    data.update(utils.flatten(data.pop('description'), 'description'))
                if series.episodes:
                    data.pop('episodes')
                    await cls._save_episodes(session, series_id, series.episodes)

                await session.execute(sa.update(Series).where(Series.id == series_id).values(**data))
                series = await session.scalar(sa.select(Series).where(Series.id == series_id))
                await session.commit()
                await cls._save_for_search(series)
                return schemas.Series.from_orm(series)

    @classmethod
    async def delete(self, series_id: int):    
        from . import Image
        async with database.session() as session:
            async with session.begin():
                await asyncio.gather(
                    session.execute(sa.delete(Series).where(Series.id == series_id)),
                    session.execute(sa.delete(Image).where(
                        Image.relation_type == 'series',
                        Image.relation_id == series_id,
                    )),
                )
                await session.commit()
                await database.es.delete(
                    index=config.data.api.elasticsearch.index_prefix+'titles',
                    id=f'series-{series_id}',
                )
            
    @staticmethod
    async def _save_externals(session: AsyncSession, series_id: str | int, externals: dict[str, str | None], patch: bool):
        current_externals = {}
        if not patch:
            await session.execute(sa.delete(Series_external).where(Series_external.show_id == series_id))
        else:
            current_externals = await session.scalar(sa.select(Series.externals).where(Series.id == series_id))

        for key in externals:
            if externals[key]:
                r = await session.scalar(sa.select(Series_external.show_id).where(
                    Series_external.title == key,
                    Series_external.value == externals[key],
                    Series_external.show_id != series_id,
                ))
                if r:
                    raise HTTPException(400, f'Series with {key}={externals[key]} already exists (Series id: {r}).')
            
            if (key not in current_externals):
                await session.execute(sa.insert(Series_external)\
                    .values(show_id=series_id, title=key, value=externals[key]))
                current_externals[key] = externals[key]
            elif (current_externals[key] != externals[key]):
                if (externals[key]):
                    await session.execute(sa.update(Series_external).where(
                        Series_external.show_id == series_id,
                        Series_external.title == key,
                    ).values(value=externals[key]))
                    current_externals[key] = externals[key]
                else:
                    await session.execute(sa.delete(Series_external).where(
                        Series_external.show_id == series_id,
                        Series_external.title == key
                    ))
                    current_externals.pop(key)
        return current_externals

    @staticmethod
    async def _save_alternative_titles(session, series_id: str | int, alternative_titles: list[str], patch: bool):
        if not patch:
            return set(alternative_titles)
        current_alternative_titles = await session.scalar(sa.select(Series.alternative_titles).where(Series.id == series_id))
        return set(current_alternative_titles + alternative_titles)

    @staticmethod
    async def _save_genres(session, series_id: str | int, genres: list[str], patch: bool):
        genres = set(genres)
        current_genres = set()
        if patch:
            current_genres = set(await session.scalar(sa.select(Series.genres).where(Series.id == series_id)))
            r_genres = current_genres | genres
        else:
            r_genres = genres
            await session.execute(sa.delete(Series_genre).where(Series_genre.show_id == series_id))
        genres = (genres - current_genres)
        if genres:
            await session.execute(sa.insert(Series_genre).prefix_with('IGNORE'), [
                {'show_id': series_id, 'genre': g} for g in genres
            ])
        return r_genres
        

    @staticmethod
    async def _save_for_search(series: "Series"):
        doc = series.title_document()
        if not doc:
            return
        await database.es.index(
            index=config.data.api.elasticsearch.index_prefix+'titles',
            id=f'series-{series.id}',
            document=doc.dict(),
        )

    @classmethod
    async def _save_episodes(cls, session: AsyncSession, series_id: int, episodes: list[schemas.Episode_create | schemas.Episode_update]):
        async def _save_episode(episode: schemas.Episode_create | schemas.Episode_update):
            e = await session.scalar(sa.select(Episode.number).where(
                Episode.show_id == series_id,
                Episode.number == episode.number,
            ))
            data = episode.dict(exclude_unset=True)
            if 'description' in data:
                data.update(utils.flatten(data.pop('description'), 'description'))
            if e != None:
                await session.execute(sa.update(Episode).values(data).where(
                    Episode.show_id == series_id,
                    Episode.number == episode.number,
                ))
            else:
                await session.execute(sa.insert(Episode).values(
                    show_id=series_id,
                    **data,
                ))
        await asyncio.gather(*[_save_episode(episode) for episode in episodes])
        await cls.update_seasons(session, series_id)

    def title_document(self) -> schemas.Search_title_document:
        if not self.title:
            return
        titles = [self.title, *self.alternative_titles]
        year = str(self.premiered.year) if self.premiered else ''
        for title in titles[:]:
            if title and year not in title:
                t = f'{title} {year}'
                if t not in titles:
                    titles.append(t)
        return schemas.Search_title_document(
            type = 'series',
            id = self.id,
            title = self.title,
            titles = [{'title': title} for title in titles],
            release_date = self.premiered,
            imdb = self.externals.get('imdb'),
            poster_image = schemas.Image.from_orm(self.poster_image) if self.poster_image else None,
        )

    @staticmethod
    async def update_seasons(session: AsyncSession, series_id: int) -> None:
        """Counts the number of episodes per season.
        Sets the value in the variable `self.seasons`.

        Must be called if one or more episodes for the show has
        been added/edited/deleted.

            [
                {
                    'season': 1,
                    'from': 1,
                    'to': 22,
                    'total': 22,
                },
                {
                    'season': 2,
                    'from': 23,
                    'to': 44,
                    'total': 22,
                }
            ]
        """
        

        rows = await session.execute(sa.select(
            Episode.season.label('season'), 
            sa.func.min(Episode.number).label('from'),
            sa.func.max(Episode.number).label('to'),
            sa.func.count(Episode.number).label('total'),
        ).where(
            Episode.show_id == series_id,
        ).group_by(Episode.season))
        seasons = []
        total_episodes = 0
        for row in rows:
            if not row['season']:
                continue
            total_episodes += row['total']
            seasons.append({
                'season': row['season'],
                'from': row['from'],
                'to': row['to'],
                'total': row['total'],
            })
        await session.execute(sa.update(Series).where(Series.id == series_id).values({
            'seasons': seasons,
            'total_episodes': total_episodes
        }))

    @staticmethod
    async def get_by_external(session: AsyncSession, external_title: str, external_value: str) -> 'Series':
        r = await session.scalars(sa.select(Series).where(
            Series_external.title == external_title,
            Series_external.value == external_value,
            Series.id == Series_external.show_id,
        ))
        if r:
            return r.first()


class Series_external(Base):
    __tablename__ = 'show_externals'

    show_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))


class Series_genre(Base):
    __tablename__ = 'show_genres'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    genre = sa.Column(sa.String(100), primary_key=True)

class Genre(Base):
    __tablename__ = 'genres'
    genre = sa.Column(sa.String(100), primary_key=True)

@rebuild_cache.register('shows')
def rebuild_shows():
    with new_session() as session:
        for item in session.query(Series).yield_per(10000):
            item.to_elasticsearch()
        session.commit()
