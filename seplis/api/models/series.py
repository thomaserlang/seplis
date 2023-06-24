import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from seplis.utils.sqlalchemy import UtcDateTime
from .episode import Episode
from .base import Base
from ..database import auto_session, database
from .. import schemas, exceptions
from ... import config, utils, constants
from .genre import Genre


class Series(Base):
    __tablename__ = 'series'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    created_at = sa.Column(UtcDateTime)
    updated_at = sa.Column(UtcDateTime)
    status = sa.Column(sa.Integer, default=0, nullable=False)
    title = sa.Column(sa.String(200))
    original_title = sa.Column(sa.String(200))
    plot = sa.Column(sa.String(2000), nullable=True)
    tagline = sa.Column(sa.String(500), nullable=True)
    premiered = sa.Column(sa.Date)
    ended = sa.Column(sa.Date)
    externals = sa.Column(sa.JSON(), default=lambda: {})
    importer_info = sa.Column(sa.String(45), nullable=True)
    importer_episodes = sa.Column(sa.String(45), nullable=True)
    seasons = sa.Column(sa.JSON(), default=lambda: [])
    runtime = sa.Column(sa.Integer, nullable=True)
    genres = sa.Column(sa.JSON(), default=lambda: [])
    alternative_titles = sa.Column(sa.JSON(), default=lambda: [])
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'), nullable=True)
    poster_image = sa.orm.relationship('Image', lazy=False)
    episode_type = sa.Column(
        sa.Integer,
        default=constants.SHOW_EPISODE_TYPE_SEASON_EPISODE,
    )
    total_episodes = sa.Column(sa.Integer, default=0)
    language = sa.Column(sa.String(100), nullable=True)
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4), nullable=True)
    rating = sa.Column(sa.DECIMAL(4, 2), nullable=True)
    rating_votes = sa.Column(sa.Integer, nullable=True)

    @property
    def importers(self):
        return {
            'info': self.importer_info,
            'episodes': self.importer_episodes,
        }

    @classmethod
    @auto_session
    async def save(cls,
        data: schemas.Series_create | schemas.Series_update,
        series_id: int | None = None,
        patch=True,
        overwrite_genres=False,
        session=None
    ):
        _data = data.dict(exclude_unset=True) if data else {}
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
            _data['genres'] = await cls._save_genres(session, series_id, _data['genres'], False if overwrite_genres else patch)
        if 'importers' in _data:
            _data.update(utils.flatten(_data.pop('importers'), 'importer'))

        if 'episodes' in _data:
            _data.pop('episodes')
            await cls._save_episodes(session, series_id, data.episodes, patch=patch)
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
                    session.execute(sa.delete(Series).where(
                        Series.id == series_id)),
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
                dup_series = await session.scalar(sa.select(Series).where(
                    Series_external.title == key,
                    Series_external.value == externals[key],
                    Series_external.series_id != series_id,
                    Series.id == Series_external.series_id,
                ))
                if dup_series:
                    raise exceptions.Series_external_duplicated(
                        external_title=key,
                        external_value=externals[key],
                        series=utils.json_loads(utils.json_dumps(
                            schemas.Series.from_orm(dup_series)))
                    )

            if (key not in current_externals):
                if externals[key]:
                    await session.execute(sa.insert(Series_external)
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
    async def _save_episodes(cls, session: AsyncSession, series_id: int, episodes: list[schemas.Episode_create | schemas.Episode_update], patch: bool):
        if not patch:
            await session.execute(sa.delete(Episode).where(Episode.series_id == series_id))
        else:
            await session.execute(sa.delete(Episode).where(
                Episode.series_id == series_id,
                Episode.number.notin_([e.number for e in episodes if e.number]),
            ))
        if not episodes:
            return
        rows = []
        for episode in episodes:
            data = episode.dict(exclude_unset=True)
            data['series_id'] = series_id
            if 'air_datetime' in data and not 'air_date' in data:
                data['air_date'] = episode.air_datetime.date() if episode.air_datetime else None
            rows.append(data)
        await session.execute(sa.insert(Episode).prefix_with('IGNORE'), rows)
        await cls.update_seasons(session, series_id)

    def title_document(self):
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
            type='series',
            id=self.id,
            title=self.title,
            titles=[schemas.Search_title_document_title(title=title) for title in titles],
            release_date=self.premiered,
            imdb=self.externals.get('imdb'),
            poster_image=schemas.Image.from_orm(
                self.poster_image) if self.poster_image else None,
            popularity=self.popularity or 0,
            genres=self.genres,
            rating=self.rating,
            rating_votes=self.rating_votes,
            episodes=self.total_episodes,
            seasons=len(self.seasons),
            runtime=self.runtime,
            language=self.language,
        )

    @staticmethod
    async def update_seasons(session: AsyncSession, series_id: int):
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
        seasons: list[schemas.Series_season] = []
        total_episodes = 0
        for row in rows:
            total_episodes += row.total
            if not row.season:
                continue
            seasons.append(schemas.Series_season(
                season=row.season,
                from_=row.from_,
                to=row.to,
                total=row.total,
            ))
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


class Series_external(Base):
    __tablename__ = 'series_externals'

    series_id = sa.Column(sa.Integer, sa.ForeignKey(
        'series.id'), primary_key=True)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))


class Series_genre(Base):
    __tablename__ = 'series_genres'

    series_id = sa.Column(sa.Integer, sa.ForeignKey(
        'series.id'), primary_key=True, autoincrement=False)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey(
        'genres.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False)


async def rebuild_series():
    async def c():
        async with database.session() as session:
            result = await session.stream(sa.select(Series))
            async for series in result.yield_per(1000):
                for s in series:
                    d = s.title_document()
                    if not d:
                        continue
                    yield {
                        '_index': config.data.api.elasticsearch.index_prefix+'titles',
                        '_id': f'series-{s.id}',
                        **d.dict()
                    }
    from elasticsearch import helpers
    await helpers.async_bulk(database.es, c())
