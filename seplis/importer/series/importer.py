import asyncio
import time
from typing import Any

import sqlalchemy as sa

from seplis import logger
from seplis.api import exceptions
from seplis.api.database import database
from seplis.api.image import (
    Image,
    ImageImport,
    MImage,
    image_mapper,
)
from seplis.api.image import (
    save_image as save_image_action,
)
from seplis.api.person import get_person_from_external
from seplis.api.series.actions.series_actions import save_series
from seplis.api.series.actions.series_cast_actions import (
    add_series_cast,
    delete_series_cast,
    series_cast_person_model_mapper,
)
from seplis.api.series.models.series_cast_model import MSeriesCast
from seplis.api.series.models.series_model import (
    MSeries,
    MSeriesExternal,
    series_mapper,
)
from seplis.api.series.schemas.episode_schemas import EpisodeUpdate
from seplis.api.series.schemas.series_cast_schemas import (
    SeriesCastPerson,
    SeriesCastPersonImport,
    SeriesCastPersonUpdate,
)
from seplis.api.series.schemas.series_schemas import Series, SeriesUpdate
from seplis.importer.people.importer import create_person

from .base import importers


async def update_series_by_id(series_id: int) -> None:
    async with database.session() as session:
        result = await session.scalar(sa.select(MSeries).where(MSeries.id == series_id))
        if not result:
            logger.error(f'Unknown series: {series_id}')
            return
        await update_series(series_mapper(result))


async def update_series_bulk(from_series_id: int = 0, do_async: bool = False) -> None:

    logger.info('Updating series')

    results = await _get_series(from_series_id)
    while results:
        for series in results:
            from_series_id = series.id
            try:
                if not do_async:
                    await update_series(series)
                else:
                    await database.redis_queue.enqueue_job(
                        'update_series', series_id=series.id
                    )
            except KeyboardInterrupt, SystemExit:
                break
            except exceptions.APIException as e:
                logger.info(e.message)
            except Exception as e:
                logger.exception(e)
        else:
            results = await _get_series(from_series_id)


async def _get_series(from_series_id: int) -> list[Series]:
    async with database.session() as session:
        query = sa.select(MSeries)
        query = query.where(MSeries.id > from_series_id).limit(100)
        results = await session.scalars(query)
        return [series_mapper(series) for series in results]


async def update_series_incremental() -> None:
    logger.info('Incremental series update started')
    if not importers:
        logger.warning('No series importers registered')
    for key in importers:
        logger.info(f'Checking importer {key}')
        try:
            await _importer_incremental(importers[key])
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception as e:
            logger.exception(e)


async def _importer_incremental(importer: Any) -> None:
    timestamp = time.time()
    external_ids = await importer.incremental_updates()
    if not external_ids:
        return
    async with database.session() as session:
        for external_id in external_ids:
            result = await session.scalar(
                sa.select(MSeries).where(
                    MSeriesExternal.title == importer.external_name,
                    MSeriesExternal.value == external_id,
                    MSeries.id == MSeriesExternal.series_id,
                )
            )
            if not result:
                logger.info(f'{importer.external_name} {external_id} not found')
                continue
            series = series_mapper(result)
            try:
                if importer.external_name in (
                    series.importers.info,
                    series.importers.episodes,
                ):
                    await update_series(series)
                else:
                    await update_series_images(series)
            except KeyboardInterrupt, SystemExit:
                raise
            except exceptions.APIException as e:
                logger.error(e.message)
            except Exception as e:
                logger.exception(e)
    importer.save_timestamp(timestamp)


async def update_series(series: Series) -> None:
    if not series.externals:
        logger.warning(f'[Series: {series.id}]: No externals')
        return
    if not series.importers:
        logger.warning(f'[Series: {series.id}] No importers')
        return
    logger.info(f'[Series: {series.id}] Updating')
    await check_external_ids(series)
    await update_series_info(series)
    await update_series_episodes(series)
    await update_series_images(series)
    await update_series_cast(series)


async def check_external_ids(series: Series) -> None:
    """If themoviedb id is missing, try and find it from imdb id"""
    if not series.externals.get('themoviedb') and series.externals.get('imdb'):
        logger.debug(f'[Series: {series.id}] Missing themoviedb, trying to find it')
        id_ = await call_importer(
            'themoviedb', 'lookup_from_imdb', series.externals['imdb']
        )
        if id_:
            logger.debug(f'[Series: {series.id}] Found themoviedb id: {id_}')
            await save_series(
                data=SeriesUpdate(
                    externals={
                        'themoviedb': id_,
                    }
                ),
                series_id=series.id,
                patch=True,
            )


async def update_series_info(series: Series) -> None:
    logger.debug(f'[Series: {series.id}] Updating info')
    if not series.importers.info:
        logger.debug(f'[Series: {series.id}] No info importer')
        return
    info: SeriesUpdate = await call_importer(
        external_name=series.importers.info,
        method='info',
        external_id=series.externals.get(series.importers.info),
    )
    if info:
        await save_series(
            data=info, series_id=series.id, patch=True, overwrite_genres=True
        )


async def update_series_episodes(series: Series) -> None:
    logger.debug(f'[Series: {series.id}] Updating episodes')
    if not series.importers.episodes:
        logger.debug(f'[Series: {series.id}] No episodes')
        return
    external_id = series.externals.get(series.importers.episodes)
    if not external_id:
        logger.debug(
            f'[Series: {series.id}] Missing externals.{series.importers.episodes}'
        )
        return
    episodes: list[EpisodeUpdate] = await call_importer(
        external_name=series.importers.episodes,
        method='episodes',
        external_id=external_id,
    )
    if episodes is not None:
        update = SeriesUpdate(episodes=episodes)
        await save_series(data=update, series_id=series.id, patch=False)


async def update_series_images(series: Series) -> None:
    logger.debug(f'[Series: {series.id}] Updating images')
    imp_names = _importers_with_support(series.externals, 'images')
    async with database.session() as session:
        result = await session.scalars(
            sa.select(MImage).where(
                MImage.relation_id == series.id,
                MImage.relation_type == 'series',
            )
        )
        current_images = {
            f'{image.external_name}-{image.external_id}': image_mapper(image)
            for image in result
        }

    async def save_image(image: ImageImport) -> None:
        try:
            if f'{image["external_name"]}-{image["external_id"]}' not in current_images:
                current_images[
                    f'{image["external_name"]}-{image["external_id"]}'
                ] = await save_image_action(
                    relation_type='series',
                    relation_id=series.id,
                    image_data=image,
                )
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception as e:
            logger.exception(e)

    for name in imp_names:
        try:
            external_id = series.externals.get(name)
            if not external_id:
                continue
            imp_images: list[ImageImport] = await call_importer(
                external_name=name,
                method='images',
                external_id=external_id,
            )
            if not imp_images:
                continue
            await asyncio.gather(*[save_image(image) for image in imp_images])
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception as e:
            logger.exception(e)

    poster: ImageImport | None = None
    if series.importers.info:
        external_id = series.externals.get(series.importers.info)
        if external_id:
            poster = await call_importer(
                external_name=series.importers.info,
                method='poster',
                external_id=external_id,
            )
    image: Image | None = None
    if poster and f'{poster["external_name"]}-{poster["external_id"]}' in current_images:
        image = current_images[f'{poster["external_name"]}-{poster["external_id"]}']
    elif not series.poster_image:
        all_images: list[Image] = list(current_images.values())
        image = all_images[0] if all_images else None

    if image:
        if not series.poster_image or series.poster_image.id != image.id:
            await save_series(
                data=SeriesUpdate(poster_image_id=image.id), series_id=series.id
            )


async def update_series_cast(series: Series) -> None:
    logger.debug(f'[Series: {series.id}] Updating cast')
    external_name = 'themoviedb'  # TODO: Should be specified per series
    if not series.externals.get(external_name):
        logger.info(
            f'[Series: {series.id}] Missing externals.{external_name} to update cast'
        )
        return
    imp_cast: list[SeriesCastPersonImport] = await call_importer(
        external_name=external_name,
        method='cast',
        external_id=series.externals[external_name],
    )
    if not imp_cast:
        logger.debug(f'[Series: {series.id}] Found no cast')
        return

    logger.debug(f'[Series: {series.id}] Found {len(imp_cast)} cast members')

    # Get existing cast
    async with database.session() as session:
        result = await session.scalars(
            sa.select(MSeriesCast).where(
                MSeriesCast.series_id == series.id,
            )
        )
        cast: dict[str, SeriesCastPerson] = {}
        for series_cast in result:
            externals = series_cast.person.externals or {}
            external_id = externals.get(external_name)
            if external_id:
                cast[f'{external_name}-{external_id}'] = series_cast_person_model_mapper(
                    series_cast
                )

    async def save_cast(member: SeriesCastPersonImport) -> None:
        try:
            key = f'{external_name}-{member["external_id"]}'
            if key not in cast:
                # Create the person if they don't "exist"
                person = await get_person_from_external(
                    external_name, member['external_id']
                )
                if not person:
                    person = await create_person(external_name, member['external_id'])
                if not person or person.id is None:
                    logger.error(
                        f'[Series: {series.id}] Failed creating cast person: '
                        f'{member["external_id"]}'
                    )
                    return
                cast[key] = SeriesCastPerson(
                    series_id=series.id,
                    person=person,
                )
            if (
                not all([r in cast[key].roles for r in member.get('roles', [])])
                or cast[key].order != member.get('order')
                or cast[key].total_episodes != member['total_episodes']
            ):
                person_id = cast[key].person.id
                if person_id is None:
                    logger.error(
                        f'[Series: {series.id}] Cast person is missing id: '
                        f'{member["external_id"]}'
                    )
                    return
                logger.debug(
                    f'[Series: {series.id}] Saving cast: {cast[key].person.name} '
                    f'({person_id})'
                )
                await add_series_cast(
                    series_id=series.id,
                    data=SeriesCastPersonUpdate(
                        person_id=person_id,
                        order=member.get('order'),
                        roles=member.get('roles', []),
                        total_episodes=member['total_episodes'],
                    ),
                )
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception:
            logger.exception(
                f'[Series: {series.id}] Failed saving cast: {member["external_id"]}'
            )

    await asyncio.gather(*[save_cast(person) for person in imp_cast])

    # Delete any cast members that don't exist anymore
    for _, member in cast.items():
        if not any(
            member.person.externals.get(m['external_name']) == m['external_id']
            for m in imp_cast
        ):
            logger.debug(
                f'[Series: {series.id}] Deleting cast: {member.person.name} '
                f'({member.person.id}))'
            )
            if member.person.id is not None:
                await delete_series_cast(series_id=series.id, person_id=member.person.id)


async def call_importer(
    external_name: str, method: str, *args: Any, **kwargs: Any
) -> Any:
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.warning(
            f'Series "{kwargs.get("external_id")}" has an unknown importer at {method} '
            f'with external name "{external_name}"'
        )
        return None
    m = getattr(im, method, None)
    if not m:
        raise Exception(f'Unknown method "{method}" for importer "{external_name}"')
    return await m(*args, **kwargs)


def _importers_with_support(externals: dict[str, str | None], support: str) -> list[str]:
    imp_names = []
    for name in importers:
        if not externals.get(name):
            continue
        if support in importers[name].supported:
            imp_names.append(name)
    return imp_names
