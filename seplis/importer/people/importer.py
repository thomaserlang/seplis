import asyncio
from typing import Any

import sqlalchemy as sa

from seplis import logger
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
from seplis.api.person import (
    MPerson,
    Person,
    PersonUpdate,
    person_mapper,
    save_person,
)
from seplis.utils.compare import compare

from .base import importers


async def update_person_by_id(person_id: int) -> None:
    async with database.session() as session:
        result = await session.scalar(sa.select(MPerson).where(MPerson.id == person_id))
        if not result:
            logger.error(f'Unknown person: {person_id}')
            return
        await update_person(person_mapper(result))


async def update_person(person: Person) -> Person | None:
    if not person.externals:
        logger.warning(f'Person {person.id} has no externals')
        return None
    logger.info(f'[Person: {person.id}] Updating')
    p = await update_person_info(person)
    if p:
        person = p
    await update_person_images(person)
    return person


async def create_person(external_name: str, external_id: str) -> Person | None:
    logger.info(f'Creating person: {external_name} {external_id}')
    return await update_person(
        person=Person(
            id=None,
            externals={
                external_name: str(external_id),
            },
        )
    )


async def update_person_info(person: Person) -> Person | None:
    # TODO: Add support for option to specify other importers like for series
    logger.debug(f'[Person: {person.id or "new"}] Updating info')
    info: PersonUpdate = await call_importer(
        external_name='themoviedb',
        method='info',
        external_id=person.externals.get('themoviedb'),
    )
    if not info:
        return None
    old_info = person.to_request()
    data = compare(info, old_info, skip_keys=['also_known_as']) if person.id else info
    missing_also_known_as = [
        x
        for x in info.get('also_known_as') or []
        if x not in (old_info.get('also_known_as') or [])
    ]
    if info.get('also_known_as') and missing_also_known_as:
        data['also_known_as'] = info['also_known_as']
    if data:
        return await save_person(
            data=PersonUpdate(**data),
            person_id=person.id,
            patch=True,
        )
    logger.debug(f'[Person: {person.id}] No info updates')
    return None


async def update_person_images(person: Person) -> None:
    logger.debug(f'[Person: {person.id}] Updating images')
    if person.id is None:
        logger.warning('Cannot update images for person without id')
        return
    person_id = person.id
    imp_names = _importers_with_support(person.externals, 'images')
    async with database.session() as session:
        result = await session.scalars(
            sa.select(MImage).where(
                MImage.relation_id == person.id,
                MImage.relation_type == 'person',
            )
        )
        current_images = {
            f'{image.external_name}-{image.external_id}': image_mapper(image)
            for image in result
        }
    images_added: list[Image] = []

    async def save_image(image: ImageImport) -> None:
        try:
            if f'{image["external_name"]}-{image["external_id"]}' not in current_images:
                images_added.append(
                    await save_image_action(
                        relation_type='person',
                        relation_id=person_id,
                        image_data=image,
                    )
                )
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception as e:
            logger.exception(e)

    imp_images: list[ImageImport] = []
    for name in imp_names:
        try:
            imp_images: list[ImageImport] = await call_importer(
                external_name=name,
                method='images',
                external_id=person.externals[name],
            )
            if not imp_images:
                continue
            await asyncio.gather(*[save_image(image) for image in imp_images])
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception:
            logger.exception(f'[Person: {person.id}] Failed saving image')

    logger.debug(f'[Person: {person.id}] Found {len(imp_images)} images')

    if not person.profile_image:
        all_images: list[Image] = []
        all_images.extend(images_added)
        all_images.extend(current_images.values())
        if all_images:
            logger.info(
                f'[Person: {person.id}] Setting new primary image: {all_images[0].id}'
            )
            await save_person(
                data=PersonUpdate(profile_image_id=all_images[0].id),
                person_id=person.id,
            )


async def call_importer(
    external_name: str, method: str, *args: Any, **kwargs: Any
) -> Any:
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.warning(
            f'Person "{kwargs.get("external_id")}" has an unknown importer at {method} '
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
