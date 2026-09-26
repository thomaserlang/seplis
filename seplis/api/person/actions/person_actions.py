from datetime import UTC, datetime
from typing import Any, cast

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis import utils
from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.image import image_columns, image_mapper
from seplis.api.image.models.image_model import MImage

from ..models.person_model import MPerson, MPersonExternal
from ..schemas.person_schemas import Person, PersonCreate, PersonUpdate


def person_mapper(person: RowMapping | MPerson) -> Person:
    if isinstance(person, MPerson):
        return Person(
            id=person.id,
            name=person.name,
            also_known_as=list(person.also_known_as or []),
            gender=person.gender,
            birthday=person.birthday,
            deathday=person.deathday,
            biography=person.biography,
            place_of_birth=person.place_of_birth,
            popularity=float(person.popularity)
            if person.popularity is not None
            else None,
            externals=dict(person.externals or {}),
            profile_image=image_mapper(person.profile_image)
            if person.profile_image
            else None,
        )
    return Person(
        id=person['id'],
        name=person['name'],
        also_known_as=list(person['also_known_as'] or []),
        gender=person['gender'],
        birthday=person['birthday'],
        deathday=person['deathday'],
        biography=person['biography'],
        place_of_birth=person['place_of_birth'],
        popularity=float(person['popularity'])
        if person['popularity'] is not None
        else None,
        externals=dict(person['externals'] or {}),
        profile_image=image_mapper(person, 'image_') if person['image_id'] else None,
    )


def select_people() -> sa.Select[Any]:
    return sa.select(MPerson.__table__, *image_columns()).outerjoin(
        MImage.__table__, MImage.id == MPerson.profile_image_id
    )


async def save_person(
    data: PersonCreate | PersonUpdate,
    person_id: int | None = None,
    patch: bool = True,
    session: AsyncSession | None = None,
) -> Person:
    values = dict(data)
    async with get_session(session) as session:
        if not person_id:
            values['created_at'] = datetime.now(tz=UTC)
            result = cast(
                Any,
                await session.execute(sa.insert(cast(sa.Table, MPerson.__table__))),
            )
            person_id = result.lastrowid
        else:
            values['updated_at'] = datetime.now(tz=UTC)

        if 'externals' in values:
            values['externals'] = await save_person_externals(
                session=session,
                person_id=person_id,
                externals=cast(dict[str, str | None], values['externals']),
                patch=patch,
            )

        if values:
            await session.execute(
                sa.update(cast(sa.Table, MPerson.__table__))
                .where(MPerson.id == person_id)
                .values(values)
            )

        person = (
            (await session.execute(select_people().where(MPerson.id == person_id)))
            .mappings()
            .first()
        )
        if not person:
            raise exceptions.NotFound('Person not found')
        return person_mapper(person)


async def create_person(data: PersonCreate) -> Person:
    return await save_person(data=data)


async def update_person(person_id: int, data: PersonUpdate) -> Person:
    return await save_person(person_id=person_id, data=data, patch=False)


async def patch_person(person_id: int, data: PersonUpdate) -> Person:
    return await save_person(person_id=person_id, data=data, patch=True)


async def get_person(person_id: int) -> Person:
    person = await get_person_optional(person_id=person_id)
    if not person:
        raise exceptions.NotFound('Person not found')
    return person


async def delete_person(person_id: int) -> None:
    async with get_session() as session:
        await session.execute(
            sa.delete(cast(sa.Table, MPerson.__table__)).where(MPerson.id == person_id)
        )


async def get_person_optional(
    person_id: int,
    session: AsyncSession | None = None,
) -> Person | None:
    async with get_session(session) as session:
        person = (
            (await session.execute(select_people().where(MPerson.id == person_id)))
            .mappings()
            .first()
        )
        if person:
            return person_mapper(person)
        return None


async def get_person_from_external(
    title: str,
    value: str,
    session: AsyncSession | None = None,
) -> Person | None:
    async with get_session(session) as session:
        person = (
            (
                await session.execute(
                    select_people().where(
                        MPerson.id == MPersonExternal.person_id,
                        MPersonExternal.title == title,
                        MPersonExternal.value == value,
                    )
                )
            )
            .mappings()
            .first()
        )
        if person:
            return person_mapper(person)
        return None


async def save_person_externals(
    session: AsyncSession,
    person_id: str | int,
    externals: dict[str, str | None],
    patch: bool,
) -> dict[str, str | None]:
    current_externals = {}
    if not patch:
        await session.execute(
            sa.delete(cast(sa.Table, MPersonExternal.__table__)).where(
                MPersonExternal.person_id == person_id
            )
        )
    else:
        current_externals = (
            await session.scalar(
                sa.select(MPerson.externals).where(MPerson.id == person_id)
            )
            or {}
        )
    for key in externals:
        if externals[key]:
            existing = (
                (
                    await session.execute(
                        select_people().where(
                            MPersonExternal.title == key,
                            MPersonExternal.value == externals[key],
                            MPersonExternal.person_id != person_id,
                            MPerson.id == MPersonExternal.person_id,
                        )
                    )
                )
                .mappings()
                .first()
            )
            if existing:
                raise exceptions.PersonExternalDuplicated(
                    external_title=key,
                    external_value=externals[key] or '',
                    person=utils.json_loads(utils.json_dumps(person_mapper(existing))),
                )

        if key not in current_externals:
            if externals[key]:
                await session.execute(
                    sa.insert(cast(sa.Table, MPersonExternal.__table__)).values(
                        person_id=person_id,
                        title=key,
                        value=externals[key],
                    )
                )
                current_externals[key] = externals[key]
        elif current_externals[key] != externals[key]:
            if externals[key]:
                await session.execute(
                    sa.update(cast(sa.Table, MPersonExternal.__table__))
                    .where(
                        MPersonExternal.person_id == person_id,
                        MPersonExternal.title == key,
                    )
                    .values(value=externals[key])
                )
                current_externals[key] = externals[key]
            else:
                await session.execute(
                    sa.delete(cast(sa.Table, MPersonExternal.__table__)).where(
                        MPersonExternal.person_id == person_id,
                        MPersonExternal.title == key,
                    )
                )
                current_externals.pop(key)
    return current_externals
