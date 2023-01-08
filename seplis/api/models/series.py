import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from .episode import Episode
from .base import Base

from ..database import auto_session, database
from .. import schemas, rebuild_cache
from ... import config, logger, utils, constants

from .series_follower import Series_follower
from .series_user_rating import Series_user_rating
from .episode import Episode, Episode_watched, Episode_last_finished
from .genre import Genre

class Series(Base):
    __tablename__ = 'series'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    updated_at = sa.Column(sa.DateTime)
    status = sa.Column(sa.Integer, default=0, nullable=False)
    title = sa.Column(sa.String(200))
    original_title = sa.Column(sa.String(200))
    plot = sa.Column(sa.String(2000))
    tagline = sa.Column(sa.String(500))
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
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4))
    rating = sa.Column(sa.DECIMAL(4, 2))


    @property
    def importers(self):
        return {
            'info': self.importer_info,
            'episodes': self.importer_episodes,
        }
 
    @classmethod
    @auto_session
    async def save(cls, data: schemas.Series_create | schemas.Series_update, series_id: int | None = None, patch=True, session=None) -> schemas.Series:
        _data = data.dict(exclude_unset=True)
        if not series_id:
            r = await session.execute(sa.insert(Series))
            series_id = r.lastrowid
            _data['created_at'] = datetime.now(tz=timezone.utc)                    
            if not data.original_title:
                _data['original_title'] = data.title
        else:
            m = await session.scalar(sa.select(Series.id).where(Series.id == series_id))
            if not m:
                raise HTTPException(404, f'Unknown series id: {series_id}')
            _data['updated_at'] = datetime.now(tz=timezone.utc)

        if 'externals' in _data:
            _data['externals'] = await cls._save_externals(session, series_id, _data['externals'], patch)
        if 'alternative_titles' in _data:
            _data['alternative_titles'] = await cls._save_alternative_titles(session, series_id, _data['alternative_titles'], patch)
        if 'genres' in _data:
            _data['genres'] = await cls._save_genres(session, series_id, _data['genres'], patch)
        if 'importers' in _data:
            _data.update(utils.flatten(_data.pop('importers'), 'importer'))

        if 'episodes' in _data:
            _data.pop('episodes')
            await cls._save_episodes(session, series_id, data.episodes)
        if _data:
            await session.execute(sa.update(Series).where(Series.id == series_id).values(**_data))
        data = await session.scalar(sa.select(Series).where(Series.id == series_id))
        await cls._save_for_search(data)
        return schemas.Series.from_orm(data)


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
            await session.execute(sa.delete(Series_external).where(Series_external.series_id == series_id))
        else:
            current_externals = await session.scalar(sa.select(Series.externals).where(Series.id == series_id))

        for key in externals:
            if externals[key]:
                r = await session.scalar(sa.select(Series_external.series_id).where(
                    Series_external.title == key,
                    Series_external.value == externals[key],
                    Series_external.series_id != series_id,
                ))
                if r:
                    raise HTTPException(400, f'Series with {key}={externals[key]} already exists (Series id: {r}).')
            
            if (key not in current_externals):
                await session.execute(sa.insert(Series_external)\
                    .values(series_id=series_id, title=key, value=externals[key]))
                current_externals[key] = externals[key]
            elif (current_externals[key] != externals[key]):
                if (externals[key]):
                    await session.execute(sa.update(Series_external).where(
                        Series_external.series_id == series_id,
                        Series_external.title == key,
                    ).values(value=externals[key]))
                    current_externals[key] = externals[key]
                else:
                    await session.execute(sa.delete(Series_external).where(
                        Series_external.series_id == series_id,
                        Series_external.title == key
                    ))
                    current_externals.pop(key)
        return current_externals

    @staticmethod
    async def _save_alternative_titles(session: AsyncSession, series_id: str | int, alternative_titles: list[str], patch: bool):
        if not patch:
            return set(alternative_titles)
        current_alternative_titles = await session.scalar(sa.select(Series.alternative_titles).where(Series.id == series_id))
        return set(current_alternative_titles + alternative_titles)

    @staticmethod
    async def _save_genres(session: AsyncSession, series_id: str | int, genres: list[str | int], patch: bool) -> list[schemas.Genre]:
        genre_ids = await Genre.get_or_create_genres(session, genres)
        current_genres: set[int] = set()
        if patch:
            current_genres = set(await session.scalars(sa.select(Series_genre.genre_id).where(Series_genre.series_id == series_id)))
        else:
            await session.execute(sa.delete(Series_genre).where(Series_genre.series_id == series_id))
        new_genre_ids = (genre_ids - current_genres)
        if new_genre_ids:
            await session.execute(sa.insert(Series_genre).prefix_with('IGNORE'), [
                {'series_id': series_id, 'genre_id': genre_id} for genre_id in new_genre_ids
            ])
        rr = await session.scalars(sa.select(Genre).where(Series_genre.series_id == series_id, Genre.id == Series_genre.genre_id).order_by(Genre.name))
        return [schemas.Genre.from_orm(r) for r in rr]

        
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
        async def _save_episode(episode_data: schemas.Episode_create | schemas.Episode_update):
            episode_number: Episode = await session.scalar(sa.select(Episode.number).where(
                Episode.series_id == series_id,
                Episode.number == episode_data.number,
            ))
            data = episode_data.dict(exclude_unset=True)
            if 'air_datetime' in data and not 'air_date' in data:
                data['air_date'] = episode_data.air_datetime.date() if episode_data.air_datetime else None
            if episode_number != None:
                await session.execute(sa.update(Episode).values(data).where(
                    Episode.series_id == series_id,
                    Episode.number == episode_data.number,
                ))
            else:
                await session.execute(sa.insert(Episode).values(
                    series_id=series_id,
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
            sa.func.min(Episode.number).label('from_'),
            sa.func.max(Episode.number).label('to'),
            sa.func.count(Episode.number).label('total'),
        ).where(
            Episode.series_id == series_id,
        ).group_by(Episode.season))
        seasons = []
        total_episodes = 0
        for row in rows:
            total_episodes += row.total
            if not row.season:
                continue
            seasons.append({
                'season': row.season,
                'from': row.from_,
                'to': row.to,
                'total': row.total,
            })
        await session.execute(sa.update(Series).where(Series.id == series_id).values(
            seasons=seasons,
            total_episodes=total_episodes,
        ))

    @staticmethod
    async def get_by_external(session: AsyncSession, external_title: str, external_value: str) -> 'Series':
        r = await session.scalars(sa.select(Series).where(
            Series_external.title == external_title,
            Series_external.value == external_value,
            Series.id == Series_external.series_id,
        ))
        if r:
            return r.first()


def series_user_query(user_id: int, sort: schemas.SERIES_USER_SORT_TYPE | None):
    last_watched_episode = sa.orm.aliased(Episode, name='last_watched_episode')
    query = sa.select(
        Series, 
        Series_user_rating.rating, 
        sa.func.IF(Series_follower.user_id != None, 1, 0).label('following'),
        Episode_watched,
        last_watched_episode,
    ).join(
        Series_user_rating, sa.and_(
            Series_user_rating.series_id == Series.id,
            Series_user_rating.user_id == user_id,
        ),
        isouter=True,
    ).join(        
        Series_follower, sa.and_(
            Series_follower.series_id == Series.id,
            Series_follower.user_id == user_id,
        ),
        isouter=True,
    ).join(        
        Episode_last_finished, sa.and_(
            Episode_last_finished.series_id == Series.id,
            Episode_last_finished.user_id == user_id,
        ),
        isouter=True,
    ).join(        
        Episode_watched, sa.and_(
            Episode_watched.series_id == Episode_last_finished.series_id,
            Episode_watched.episode_number == Episode_last_finished.episode_number,
            Episode_watched.user_id == Episode_last_finished.user_id,
        ),
        isouter=True,
    ).join(        
        last_watched_episode, sa.and_(
            last_watched_episode.series_id == Episode_last_finished.series_id,
            last_watched_episode.number == Episode_last_finished.episode_number,
        ),
        isouter=True,
    )

    if sort == 'user_rating_desc':
        query = query.order_by(
            sa.desc(Series_user_rating.rating),
            sa.desc(Series.id),
        )
    elif sort == 'user_rating_asc':
        query = query.order_by(
            sa.asc(Series_user_rating.rating),
            sa.asc(Series.id),
        )
    elif sort == 'followed_at_desc':
        query = query.order_by(
            sa.desc(Series_follower.created_at),
            sa.desc(Series.id),
        )
    elif sort == 'followed_at_asc':
        query = query.order_by(
            sa.asc(Series_follower.created_at),
            sa.asc(Series.id),
        )
    elif sort == 'watched_at_desc':
        query = query.order_by(
            sa.desc(Episode_watched.watched_at),
            sa.desc(Series.id),
        )
    elif sort == 'watched_at_asc':
        query = query.order_by(
            sa.asc(Episode_watched.watched_at),
            sa.asc(Series.id),
        )

    return query

def series_user_result_parse(row: any):
    return schemas.Series_user(
        series=schemas.Series.from_orm(row.Series),
        rating=row.rating,
        following=row.following == 1,
        last_episode_watched=schemas.Episode.from_orm(row.last_watched_episode) if row.last_watched_episode else None,
        last_episode_watched_data=schemas.Episode_watched.from_orm(row.Episode_watched) if row.Episode_watched else None,
    )
    

class Series_external(Base):
    __tablename__ = 'series_externals'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))


class Series_genre(Base):
    __tablename__ = 'series_genres'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True, autoincrement=False)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey('genres.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False)


@rebuild_cache.register('shows')
def rebuild_shows():
    with new_session() as session:
        for item in session.query(Series).yield_per(10000):
            item.to_elasticsearch()
        session.commit()
