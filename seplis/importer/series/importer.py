import time
import sqlalchemy as sa
import asyncio
from seplis import logger
from seplis.api.database import database
from seplis.api import exceptions, models, schemas
from seplis.importer.people.importer import create_person
from .base import importers


async def update_series_by_id(series_id):
    async with database.session() as session:
        result = await session.scalar(sa.select(models.Series).where(models.Series.id == series_id))
        if not result:
            logger.error(f'Unknown series: {series_id}')
        await update_series(schemas.Series.model_validate(result))


async def update_series_bulk(from_series_id=0, do_async=False):

    logger.info('Updating series')
    
    results = await _get_series(from_series_id)
    while results:
        for series in results:
            from_series_id = series.id
            try:
                if not do_async:
                    await update_series(schemas.Series.model_validate(series))
                else:
                    await database.redis_queue.enqueue_job('update_series', series_id=series.id)
            except (KeyboardInterrupt, SystemExit):
                break
            except exceptions.API_exception as e:
                logger.info(e.message)
            except Exception as e:
                logger.exception(e)
        else:
            results = await _get_series(from_series_id)
        

async def _get_series(from_series_id: int):
    async with database.session() as session:
        query = sa.select(models.Series)
        query = query.where(models.Series.id > from_series_id).limit(100)
        results = await session.scalars(query)
        return [schemas.Series.model_validate(series) for series in results]


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
                logger.info(f'{importer.external_name} {external_id} not found')
                continue
            series = schemas.Series.model_validate(result)
            try:
                if importer.external_name in series.importers.model_dump().values():
                    await update_series(series)
                else:
                    await update_series_images(series)
            except (KeyboardInterrupt, SystemExit):
                raise
            except exceptions.API_exception as e:
                logger.error(e.message)
            except Exception as e:
                logger.exception('_importer_incremental')
    importer.save_timestamp(timestamp)


async def update_series(series: schemas.Series):
    if not series.externals:
        logger.warn(f'[Series: {series.id}]: No externals')
        return
    if not series.importers:
        logger.warn(f'[Series: {series.id}] No importers')
        return    
    logger.info(f'[Series: {series.id}] Updating')
    await check_external_ids(series)
    await update_series_info(series)
    await update_series_episodes(series)
    await update_series_images(series)
    await update_series_cast(series)


async def check_external_ids(series: schemas.Series):
    '''If themoviedb id is missing, try and find it from imdb id'''
    if not series.externals.get('themoviedb') and series.externals.get('imdb'):
        logger.debug(f'[Series: {series.id}] Missing themoviedb, trying to find it')
        id_ = await call_importer('themoviedb', 'lookup_from_imdb', series.externals['imdb'])
        if id_:
            logger.debug(f'[Series: {series.id}] Found themoviedb id: {id_}')
            await models.Series.save(
                data=schemas.Series_update(externals={
                    'themoviedb': id_,
                }),
                series_id=series.id,
                patch=True,
            )


async def update_series_info(series: schemas.Series):
    logger.debug(f'[Series: {series.id}] Updating info')
    if not series.importers.info:
        logger.debug(f'[Series: {series.id}] No info importer')
        return
    info: schemas.Series_update = await call_importer(
        external_name=series.importers.info,
        method='info',
        external_id=series.externals.get(series.importers.info),
    )
    if info:
        await models.Series.save(data=info, series_id=series.id, patch=True, overwrite_genres=True)


async def update_series_episodes(series: schemas.Series):
    logger.debug(f'[Series: {series.id}] Updating episodes')
    if not series.importers.episodes:
        logger.debug(f'[Series: {series.id}] No episodes importer')
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
    logger.debug(f'[Series: {series.id}] Updating images')
    imp_names = _importers_with_support(series.externals, 'images')
    async with database.session() as session:
        result = await session.scalars(sa.select(models.Image).where(
            models.Image.relation_id == series.id,
            models.Image.relation_type == 'series',
        ))
        current_images = {
            f'{image.external_name}-{image.external_id}': schemas.Image.model_validate(image) for image in result}
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


async def update_series_cast(series: schemas.Series):
    logger.debug(f'[Series: {series.id}] Updating cast')
    external_name = 'themoviedb' # TODO: Should be specified per series
    if not series.externals.get(external_name):
        logger.info(f'[Series: {series.id}] Missing externals.{external_name} to update cast')
        return
    imp_cast: list[schemas.Series_cast_person_import] = await call_importer(
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
        result = await session.scalars(sa.select(models.Series_cast).where(
            models.Series_cast.series_id == series.id,
        ))
        cast: dict[str, schemas.Series_cast_person] = {f'{external_name}-{cast.person.externals[external_name]}': 
                schemas.Series_cast_person.model_validate(cast) for cast in result \
                    if cast.person.externals.get(external_name)}
    
    async def save_cast(member: schemas.Series_cast_person_import):
        try:
            key = f'{external_name}-{member.external_id}'
            if key not in cast:
                # Create the person if they don't "exist"
                person = await models.Person.get_from_external(external_name, member.external_id)
                if not person:
                    person = await create_person(external_name, member.external_id)
                cast[key] = schemas.Series_cast_person(
                    series_id=series.id,
                    person=person,
                    character=None,
                )
            if not all([r in cast[key].roles for r in member.roles]) or \
                cast[key].order != member.order or \
                cast[key].total_episodes != member.total_episodes:
                logger.debug(f'[Series: {series.id}] Saving cast: {cast[key].person.name} ({cast[key].person.id})')
                await models.Series_cast.save(
                    data=schemas.Series_cast_person_update(
                        series_id=series.id,
                        person_id=cast[key].person.id,
                        order=member.order,
                        roles=member.roles,
                        total_episodes=member.total_episodes,
                    )
                )
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception(f'[Series: {series.id}] Failed saving cast: {member.external_id}')

    await asyncio.gather(*[save_cast(person) for person in imp_cast])

    # Delete any cast members that don't exist anymore
    for key, member in cast.items():
        if not any(member.person.externals.get(m.external_name) == m.external_id for m in imp_cast):
            logger.debug(f'[Series: {series.id}] Deleting cast: {member.person.name} ({member.person.id}))')
            await models.Series_cast.delete(series_id=series.id, person_id=member.person.id)


async def call_importer(external_name: str, method: str, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.warn(
            f'Series "{kwargs.get("external_id")}" has an unknown importer at {method} '
            f'with external name "{external_name}"'
        )
        return
    m = getattr(im, method, None)
    if not m:
        raise Exception(f'Unknown method "{method}" for importer "{external_name}"')
    return await m(*args, **kwargs)


def _importers_with_support(externals: dict[str, str], support: str) -> list[str]:
    imp_names = []
    for name in importers:
        if name not in externals:
            continue
        if support in importers[name].supported:
            imp_names.append(name)
    return imp_names