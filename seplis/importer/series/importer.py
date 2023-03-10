import time
import sqlalchemy as sa
import asyncio
from seplis import logger
from seplis.api.database import database
from seplis.api import exceptions, models, schemas
from .base import importers


async def update_series_by_id(series_id):
    async with database.session() as session:
        result = await session.scalar(sa.select(models.Series).where(models.Series.id == series_id))
        if not result:
            logger.error(f'Unknown series: {series_id}')
        await update_series(schemas.Series.from_orm(result))


async def update_series_bulk(from_series_id=None, do_async=False):
    logger.info('Updating series')
    try:
        async with database.session() as session:
            query = sa.select(models.Series)
            if from_series_id:
                query = query.where(models.Series.id >= from_series_id)
            result = await session.stream(query)
            async for db_series in result.yield_per(500):
                for series in db_series:
                    try:
                        if not do_async:
                            from_series_id = series.id
                            await update_series(schemas.Series.from_orm(series))
                        else:
                            await database.redis_queue.enqueue_job('update_series', series_id=series.id)
                    except (KeyboardInterrupt, SystemExit):
                        break
                    except Exception as e:
                        logger.exception(e)
    except sa.exc.OprationalError as e:
        logger.exception(e)
        if from_series_id:
            update_series_bulk(from_series_id=from_series_id)



async def update_series_incremental():
    logger.info('Incremental series update started')
    if not importers:
        logger.warn('No series importers registered')
    for key in importers:
        logger.info(f'Checking importer {key}')
        try:
            await _importer_incremental(importers[key])
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            logger.exception(e)


async def _importer_incremental(importer):
    timestamp = time.time()
    external_ids = await importer.incremental_updates()
    if not external_ids:
        return
    async with database.session() as session:
        for external_id in external_ids:
            result = await session.scalar(sa.select(models.Series).where(
                models.Series_external.title == importer.external_name,
                models.Series_external.value == external_id,
                models.Series.id == models.Series_external.series_id,
            ))
            if not result:
                continue
            series = schemas.Series.from_orm(result)
            try:
                if importer.external_name in series.importers.dict().values():
                    await update_series(series)
                else:
                    await update_series_images(series)
            except (KeyboardInterrupt, SystemExit):
                raise
            except exceptions.API_exception as e:
                logger.error(e.message)
            except Exception as e:
                logger.exception(e)
    importer.save_timestamp(timestamp)


async def update_series(series: schemas.Series):
    if not series.externals:
        logger.warn(f'Series {series.id} has no externals')
        return
    if not series.importers:
        logger.warn(f'Series {series.id} has no importers')
        return
    logger.info(f'Updating series: {series.id}')
    await check_external_ids(series)
    await update_series_info(series)
    await update_series_episodes(series)
    await update_series_images(series)


async def check_external_ids(series: schemas.Series):
    if not series.externals.get('themoviedb') and series.externals.get('imdb'):
        id_ = await call_importer('themoviedb', 'lookup_from_imdb', series.externals['imdb'])
        if id_:
            await models.Series.save(
                data=schemas.Series_update(externals={
                    'themoviedb': id_,
                }),
                series_id=series.id,
                patch=True,
            )


async def update_series_info(series: schemas.Series):
    if not series.importers.info:
        return
    info: schemas.Series_update = await call_importer(
        external_name=series.importers.info,
        method='info',
        external_id=series.externals.get(series.importers.info),
    )
    if info:
        await models.Series.save(data=info, series_id=series.id, patch=True, overwrite_genres=True)


async def update_series_episodes(series: schemas.Series):
    if not series.importers.episodes:
        return
    episodes: list[schemas.Episode_create] = await call_importer(
        external_name=series.importers.episodes,
        method='episodes',
        external_id=series.externals[series.importers.episodes],
    )
    if episodes != None:
        update = schemas.Series_update(episodes=episodes)
        await models.Series.save(data=update, series_id=series.id, patch=False)


async def update_series_images(series: schemas.Series):
    if series.poster_image:
        # Need a better way to only download images in the
        # correct size from THETVDB.
        # Right now a lot of time and bandwidth is spent redownloading
        # the same images just to find out that they are not 680x1000...
        # So for now only get the images if there is no poster set for the show.
        return
    imp_names = _importers_with_support(series.externals, 'images')
    async with database.session() as session:
        result = await session.scalars(sa.select(models.Image).where(
            models.Image.relation_id == series.id,
            models.Image.relation_type == 'series',
        ))
        current_images = {
            f'{image.external_name}-{image.external_id}': schemas.Image.from_orm(image) for image in result}
    images_added: list[schemas.Image] = []

    async def save_image(image):
        try:
            if f'{image.external_name}-{image.external_id}' not in current_images:
                images_added.append(await models.Image.save(
                    relation_type='series',
                    relation_id=series.id,
                    image_data=image,
                ))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception('save_image')

    for name in imp_names:
        try:
            imp_images: list[schemas.Image_import] = await call_importer(
                external_name=name,
                method='images',
                external_id=series.externals[name],
            )
            if not imp_images:
                continue
            await asyncio.gather(*[save_image(image) for image in imp_images])
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception('update_show_images')

    if not series.poster_image:
        all_images: list[schemas.Image] = []
        all_images.extend(images_added)
        all_images.extend(current_images.values())
        if all_images:
            await models.Series.save(
                data=schemas.Series_update(
                    poster_image_id=all_images[0].id
                ),
                series_id=series.id
            )


def _importers_with_support(show_externals, support):
    """
    :returns: list of str
    """
    imp_names = []
    for name in importers:
        if name not in show_externals:
            continue
        if support in importers[name].supported:
            imp_names.append(name)
    return imp_names


async def call_importer(external_name, method, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.warn(
            'Series "{}" has an unknown importer at {} '
            'with external name "{}"'.format(
                kwargs.get('external_id'),
                method,
                external_name,
            )
        )
        return
    m = getattr(im, method, None)
    if not m:
        raise Exception('Unknown method "{}" for importer "{}"'.format(
            method,
            external_name
        ))
    return await m(*args, **kwargs)
