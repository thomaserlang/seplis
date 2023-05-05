import sqlalchemy as sa
import asyncio
from seplis import logger
from seplis.api.database import database
from seplis.api import models, schemas
from .base import importers


async def update_person_by_id(person_id):
    async with database.session() as session:
        result = await session.scalar(sa.select(models.Person).where(models.Person.id == person_id))
        if not result:
            logger.error(f'Unknown person: {person_id}')
        await update_person(schemas.Person.from_orm(result))


async def update_person(person: schemas.Person):
    if not person.externals:
        logger.warn(f'Person {person.id} has no externals')
        return
    logger.info(f'Updating person: {person.id}')
    await update_person_info(person)
    await update_person_images(person)


async def create_person(external_name: str, external_id: str):
    logger.info(f'Creating person: {external_name} {external_id}')
    return await update_person_info(person=schemas.Person(id=None, externals={
        external_name: external_id,
    }))


async def update_person_info(person: schemas.Person):
    # TODO: Add support for option to specify other importers like for series
    info: schemas.Person_update = await call_importer(
        external_name='themoviedb',
        method='info',
        external_id=person.externals.get('themoviedb'),
    )
    if info:
        return await models.Person.save(data=info, person_id=person.id, patch=True)


async def update_person_images(person: schemas.Person):
    imp_names = _importers_with_support(person.externals, 'images')
    async with database.session() as session:
        result = await session.scalars(sa.select(models.Image).where(
            models.Image.relation_id == person.id,
            models.Image.relation_type == 'person',
        ))
        current_images = {
            f'{image.external_name}-{image.external_id}': schemas.Image.from_orm(image) for image in result}
    images_added: list[schemas.Image] = []

    async def save_image(image):
        try:
            if f'{image.external_name}-{image.external_id}' not in current_images:
                images_added.append(await models.Image.save(
                    relation_type='person',
                    relation_id=person.id,
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
                external_id=person.externals[name],
            )
            if not imp_images:
                continue
            await asyncio.gather(*[save_image(image) for image in imp_images])
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception('update_show_images')

    if not person.profile_image:
        all_images: list[schemas.Image] = []
        all_images.extend(images_added)
        all_images.extend(current_images.values())
        if all_images:
            await models.Person.save(
                data=schemas.Series_update(
                    poster_image_id=all_images[0].id
                ),
                person_id=person.id
            )


async def call_importer(external_name: str, method: str, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.warn(
            f'Person "{kwargs.get("external_id")}" has an unknown importer at {method} '
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