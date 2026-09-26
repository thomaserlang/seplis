from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast

import sqlalchemy as sa
from fastapi import HTTPException

from seplis import config, utils
from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.database import database
from seplis.api.genre import Genre, MGenre, genre_mapper, get_or_create_genres
from seplis.api.image import MImage
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.search import SearchTitleDocument, SearchTitleDocumentTitle
from seplis.api.user import UserAuthenticated

from ..models.episode_model import MEpisode
from ..models.series_model import (
    MSeries,
    MSeriesExternal,
    MSeriesGenre,
)
from ..schemas.episode_schemas import EpisodeCreate, EpisodeUpdate
from ..schemas.series_schemas import Series, SeriesCreate, SeriesSeason, SeriesUpdate
from ..types.series_filter_types import SeriesQueryFilter
from .series_expand_actions import expand_series
from .series_filter_actions import filter_series
from .series_mapping import select_series, series_row_mapper


async def get_series(
    page_cursor: PageCursorQuery,
    filter_query: SeriesQueryFilter,
    session: AsyncSession | None = None,
) -> PageCursor[Series]:
    return await filter_series(
        query=select_series(),
        session=session,
        filter_query=filter_query,
        page_query=page_cursor,
    )


async def get_series_one(
    series_id: int,
    expand: list[str] | None,
    user: UserAuthenticated | None,
    session: AsyncSession | None = None,
) -> Series:
    async with get_session(session) as session:
        series = (
            (await session.execute(select_series().where(MSeries.id == series_id)))
            .mappings()
            .first()
        )
        if not series:
            raise exceptions.NotFound('Unknown series')
        result = series_row_mapper(series)
        await expand_series(series=[result], user=user, expand=expand)
        return result


async def get_series_by_external(
    external_name: str,
    external_id: str,
    session: AsyncSession | None = None,
) -> Series:
    async with get_session(session) as session:
        series = (
            (
                await session.execute(
                    select_series().where(
                        MSeriesExternal.title == external_name,
                        MSeriesExternal.value == external_id,
                        MSeries.id == MSeriesExternal.series_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        if not series:
            raise exceptions.NotFound('Unknown series')
        return series_row_mapper(series)


async def create_series(data: SeriesCreate) -> Series:
    series = await save_series(data, series_id=None, patch=False)
    await database.redis_queue.enqueue_job('update_series', int(series.id))
    return series


async def update_series(series_id: int, data: SeriesUpdate) -> Series:
    return await save_series(series_id=series_id, data=data, patch=False)


async def patch_series(series_id: int, data: SeriesUpdate) -> Series:
    return await save_series(series_id=series_id, data=data, patch=True)


async def delete_series(series_id: int) -> None:
    async with get_session() as session:
        await session.execute(
            sa.delete(cast(sa.Table, MSeries.__table__)).where(MSeries.id == series_id)
        )
        await session.execute(
            sa.delete(cast(sa.Table, MImage.__table__)).where(
                MImage.relation_type == 'series',
                MImage.relation_id == series_id,
            )
        )
    await database.es.delete(
        index=config.api.elasticsearch.index_prefix + 'titles',
        id=f'series-{series_id}',
    )


async def request_series_update(series_id: int) -> None:
    await database.redis_queue.enqueue_job('update_series', series_id)


async def save_series(
    data: SeriesCreate | SeriesUpdate,
    series_id: int | None = None,
    patch: bool = True,
    overwrite_genres: bool = False,
    session: AsyncSession | None = None,
) -> Series:
    values = dict(data or {})
    async with get_session(session) as session:
        if not series_id:
            result = cast(
                Any,
                await session.execute(sa.insert(cast(sa.Table, MSeries.__table__))),
            )
            series_id = result.lastrowid
            values['created_at'] = datetime.now(tz=UTC)
            if not values.get('original_title'):
                values['original_title'] = values.get('title')
        else:
            exists = await session.scalar(
                sa.select(MSeries.id).where(MSeries.id == series_id)
            )
            if not exists:
                raise HTTPException(404, f'Unknown series id: {series_id}')
            values['updated_at'] = datetime.now(tz=UTC)

        if 'externals' in values:
            values['externals'] = await save_series_externals(
                session=session,
                series_id=series_id,
                externals=values['externals'],
                patch=patch,
            )
        if 'alternative_titles' in values:
            values['alternative_titles'] = await save_series_alternative_titles(
                session=session,
                series_id=series_id,
                alternative_titles=values['alternative_titles'],
                patch=patch,
            )
        if 'genre_names' in values:
            values['genres'] = await save_series_genres(
                session=session,
                series_id=series_id,
                genres=values.pop('genre_names'),
                patch=False if overwrite_genres else patch,
            )
        if 'importers' in values:
            values.update(utils.flatten(values.pop('importers'), 'importer'))
        if values.get('rating') and values.get('rating_votes'):
            values['rating_weighted'] = utils.calculate_weighted_rating(
                values['rating'], values['rating_votes']
            )

        if 'episodes' in values:
            episodes = values.pop('episodes')
            await save_series_episodes(
                session=session,
                series_id=series_id,
                episodes=episodes,
                patch=patch,
            )
        if values:
            await session.execute(
                sa.update(cast(sa.Table, MSeries.__table__))
                .where(MSeries.id == series_id)
                .values(**values)
            )
        series = (
            (await session.execute(select_series().where(MSeries.id == series_id)))
            .mappings()
            .first()
        )
        if not series:
            raise HTTPException(404, f'Unknown series id: {series_id}')
        mapped_series = series_row_mapper(series)
        await save_series_for_search(mapped_series)
        return mapped_series


async def save_series_externals(
    session: AsyncSession,
    series_id: str | int,
    externals: dict[str, str | None],
    patch: bool,
) -> dict[str, str | None]:
    current_externals = {}
    if not patch:
        await session.execute(
            sa.delete(cast(sa.Table, MSeriesExternal.__table__)).where(
                MSeriesExternal.series_id == series_id
            )
        )
    else:
        current_externals = (
            await session.scalar(
                sa.select(MSeries.externals).where(MSeries.id == series_id)
            )
            or {}
        )

    for key in externals:
        if externals[key]:
            duplicate_series = (
                (
                    await session.execute(
                        select_series().where(
                            MSeriesExternal.title == key,
                            MSeriesExternal.value == externals[key],
                            MSeriesExternal.series_id != series_id,
                            MSeries.id == MSeriesExternal.series_id,
                        )
                    )
                )
                .mappings()
                .first()
            )
            if duplicate_series:
                raise exceptions.SeriesExternalDuplicated(
                    external_title=key,
                    external_value=externals[key] or '',
                    series=utils.json_loads(
                        utils.json_dumps(series_row_mapper(duplicate_series))
                    ),
                )

        if key not in current_externals:
            if externals[key]:
                await session.execute(
                    sa.insert(cast(sa.Table, MSeriesExternal.__table__)).values(
                        series_id=series_id,
                        title=key,
                        value=externals[key],
                    )
                )
                current_externals[key] = externals[key]
        elif current_externals[key] != externals[key]:
            if externals[key]:
                await session.execute(
                    sa.update(cast(sa.Table, MSeriesExternal.__table__))
                    .where(
                        MSeriesExternal.series_id == series_id,
                        MSeriesExternal.title == key,
                    )
                    .values(value=externals[key])
                )
                current_externals[key] = externals[key]
            else:
                await session.execute(
                    sa.delete(cast(sa.Table, MSeriesExternal.__table__)).where(
                        MSeriesExternal.series_id == series_id,
                        MSeriesExternal.title == key,
                    )
                )
                current_externals.pop(key)
    return current_externals


async def save_series_alternative_titles(
    session: AsyncSession,
    series_id: str | int,
    alternative_titles: list[str],
    patch: bool,
) -> set[str]:
    if not patch:
        return set(alternative_titles)
    current_alternative_titles = (
        await session.scalar(
            sa.select(MSeries.alternative_titles).where(MSeries.id == series_id)
        )
        or []
    )
    return set(current_alternative_titles + alternative_titles)


async def save_series_genres(
    session: AsyncSession,
    series_id: str | int,
    genres: list[str | int],
    patch: bool,
) -> list[Genre]:
    genre_ids = await get_or_create_genres(genres, type_='series')
    current_genres: set[int] = set()
    if patch:
        current_genres = set(
            await session.scalars(
                sa.select(MSeriesGenre.genre_id).where(
                    MSeriesGenre.series_id == series_id
                )
            )
        )
    else:
        await session.execute(
            sa.delete(cast(sa.Table, MSeriesGenre.__table__)).where(
                MSeriesGenre.series_id == series_id
            )
        )
    new_genre_ids = genre_ids - current_genres
    if new_genre_ids:
        await session.execute(
            sa.insert(cast(sa.Table, MSeriesGenre.__table__)).prefix_with('IGNORE'),
            [
                {'series_id': series_id, 'genre_id': genre_id}
                for genre_id in new_genre_ids
            ],
        )
    if genre_ids != current_genres:
        await session.execute(
            sa.text(
                'update genres set number_of = (select count(genres.id) '
                'from series_genres where series_genres.genre_id = genres.id) '
                'where type="series"'
            )
        )
    rows = (
        await session.execute(
            sa.select(MGenre.__table__)
            .where(
                MSeriesGenre.series_id == series_id,
                MGenre.id == MSeriesGenre.genre_id,
            )
            .order_by(MGenre.name)
        )
    ).mappings()
    return [genre_mapper(row) for row in rows]


async def save_series_episodes(
    session: AsyncSession,
    series_id: int,
    episodes: list[EpisodeCreate | EpisodeUpdate],
    patch: bool,
) -> None:
    if not patch:
        await session.execute(
            sa.delete(cast(sa.Table, MEpisode.__table__)).where(
                MEpisode.series_id == series_id
            )
        )
    else:
        await session.execute(
            sa.delete(cast(sa.Table, MEpisode.__table__)).where(
                MEpisode.series_id == series_id,
                MEpisode.number.notin_(
                    [episode['number'] for episode in episodes if episode.get('number')]
                ),
            )
        )
    if not episodes:
        return
    episode_columns = tuple(column.name for column in MEpisode.__table__.columns)
    rows: list[dict[str, Any]] = []
    for episode in episodes:
        values = dict(episode)
        values['series_id'] = series_id
        air_datetime = cast(datetime | None, values.get('air_datetime'))
        if air_datetime and 'air_date' not in values:
            values['air_date'] = air_datetime.date()
        rows.append({column: values.get(column) for column in episode_columns})

    await session.execute(
        sa.insert(cast(sa.Table, MEpisode.__table__)).prefix_with('IGNORE'),
        rows,
    )
    await update_series_seasons(session=session, series_id=series_id)


async def update_series_seasons(session: AsyncSession, series_id: int) -> None:
    rows = (
        await session.execute(
            sa.select(
                MEpisode.season.label('season'),
                sa.func.min(MEpisode.number).label('from_'),
                sa.func.max(MEpisode.number).label('to'),
                sa.func.count(MEpisode.number).label('total'),
            )
            .where(
                MEpisode.series_id == series_id,
            )
            .group_by(MEpisode.season)
        )
    ).mappings()
    seasons: list[SeriesSeason] = []
    total_episodes = 0
    for row in rows:
        total_episodes += row['total']
        if not row['season']:
            continue
        seasons.append(
            SeriesSeason(
                season=row['season'],
                from_=row['from_'],
                to=row['to'],
                total=row['total'],
            )
        )
    await session.execute(
        sa.update(cast(sa.Table, MSeries.__table__))
        .where(MSeries.id == series_id)
        .values(
            seasons=seasons,
            total_episodes=total_episodes,
        )
    )


async def save_series_for_search(series: Series) -> None:
    document = series_title_document_mapper(series)
    if not document:
        return
    await database.es.index(
        index=config.api.elasticsearch.index_prefix + 'titles',
        id=f'series-{series.id}',
        document=utils.json_loads(utils.json_dumps(document)),
    )


def series_title_document_mapper(series: Series) -> SearchTitleDocument | None:
    if not series.title:
        return None
    titles = [series.title, *(series.alternative_titles or [])]
    year = str(series.premiered.year) if series.premiered else ''
    for title in titles[:]:
        if title and year not in title:
            title_with_year = f'{title} {year}'
            if title_with_year not in titles:
                titles.append(title_with_year)
    return SearchTitleDocument(
        type='series',
        id=series.id,
        title=series.title,
        titles=[SearchTitleDocumentTitle(title=title) for title in titles],
        release_date=series.premiered,
        imdb=(series.externals or {}).get('imdb'),
        poster_image=series.poster_image,
        popularity=float(series.popularity or 0),
        genres=genres_from_values(series.genres),
        rating=float(series.rating) if series.rating is not None else None,
        rating_votes=series.rating_votes,
        episodes=series.total_episodes,
        seasons=len(series.seasons or []),
        runtime=series.runtime,
        language=series.language,
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


async def rebuild_series() -> None:
    async def documents() -> AsyncIterator[dict[str, Any]]:
        async with database.session() as session:
            result = await session.stream(select_series())
            async for series in result.mappings().partitions(1000):
                for row in series:
                    item = series_row_mapper(row)
                    document = series_title_document_mapper(item)
                    if not document:
                        continue
                    yield {
                        '_index': config.api.elasticsearch.index_prefix + 'titles',
                        '_id': f'series-{item.id}',
                        **utils.json_loads(utils.json_dumps(document)),
                    }

    from elasticsearch import helpers

    await helpers.async_bulk(database.es, documents())
