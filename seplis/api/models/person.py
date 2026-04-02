from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ... import utils
from .. import exceptions, schemas
from ..database import AsyncSession, auto_session
from .base import Base

if TYPE_CHECKING:
    from .image import MImage


class MPerson(Base):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(sa.DateTime)
    name: Mapped[str] = mapped_column(sa.String(500))
    also_known_as: Mapped[list | None] = mapped_column(sa.JSON)
    gender: Mapped[int | None] = mapped_column(sa.SMALLINT)
    birthday: Mapped[date | None] = mapped_column(sa.Date)
    deathday: Mapped[date | None] = mapped_column(sa.Date)
    biography: Mapped[str | None] = mapped_column(sa.String(2000))
    place_of_birth: Mapped[str | None] = mapped_column(sa.String(100))
    popularity: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(precision=12, scale=4))
    externals: Mapped[dict | None] = mapped_column(sa.JSON)
    profile_image_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('images.id', onupdate='cascade', ondelete='set null')
    )
    profile_image: Mapped[MImage | None] = relationship('MImage', lazy=False)

    @classmethod
    @auto_session
    async def save(
        cls,
        data,
        person_id: int = None,
        patch: bool = True,
        session: AsyncSession = None,
    ):
        _data = data.model_dump(exclude_unset=True)
        if not person_id:
            _data['created_at'] = datetime.now(tz=UTC)
            r = await session.execute(sa.insert(MPerson))
            person_id = r.lastrowid
        else:
            _data['updated_at'] = datetime.now(tz=UTC)

        if 'externals' in _data:
            _data['externals'] = await cls._save_externals(
                session, person_id, _data['externals'], patch
            )

        if _data:
            await session.execute(
                sa.update(MPerson).where(MPerson.id == person_id).values(_data)
            )

        person = await session.scalar(sa.select(MPerson).where(MPerson.id == person_id))
        return schemas.Person.model_validate(person)

    @staticmethod
    @auto_session
    async def delete(person_id: int, session: AsyncSession = None) -> None:
        await session.execute(sa.delete(MPerson).where(MPerson.id == person_id))

    @staticmethod
    @auto_session
    async def get_from_external(
        title: str,
        value: str,
        session: AsyncSession = None,
    ):
        person = await session.scalar(
            sa.select(MPerson).where(
                MPerson.id == MPersonExternal.person_id,
                MPersonExternal.title == title,
                MPersonExternal.value == value,
            )
        )
        if person:
            return schemas.Person.model_validate(person)
        return None

    @staticmethod
    @auto_session
    async def get(person_id: int, session: AsyncSession = None):
        person = await session.scalar(sa.select(MPerson).where(MPerson.id == person_id))
        if person:
            return schemas.Person.model_validate(person)
        return None

    @staticmethod
    async def _save_externals(
        session: AsyncSession,
        person_id: str | int,
        externals: dict[str, str | None],
        patch: bool,
    ):
        current_externals = {}
        if not patch:
            await session.execute(
                sa.delete(MPersonExternal).where(MPersonExternal.person_id == person_id)
            )
        else:
            current_externals = await session.scalar(
                sa.select(MPerson.externals).where(MPerson.id == person_id)
            )
        for key in externals:
            if externals[key]:
                r = await session.scalar(
                    sa.select(MPerson).where(
                        MPersonExternal.title == key,
                        MPersonExternal.value == externals[key],
                        MPersonExternal.person_id != person_id,
                        MPerson.id == MPersonExternal.person_id,
                    )
                )
                if r:
                    raise exceptions.Person_external_duplicated(
                        external_title=key,
                        external_value=externals[key],
                        person=utils.json_loads(
                            utils.json_dumps(schemas.Person.model_validate(r))
                        ),
                    )

            if key not in current_externals:
                if externals[key]:
                    await session.execute(
                        sa.insert(MPersonExternal).values(
                            person_id=person_id, title=key, value=externals[key]
                        )
                    )
                    current_externals[key] = externals[key]
            elif current_externals[key] != externals[key]:
                if externals[key]:
                    await session.execute(
                        sa.update(MPersonExternal)
                        .where(
                            MPersonExternal.person_id == person_id,
                            MPersonExternal.title == key,
                        )
                        .values(value=externals[key])
                    )
                    current_externals[key] = externals[key]
                else:
                    await session.execute(
                        sa.delete(MPersonExternal).where(
                            MPersonExternal.person_id == person_id,
                            MPersonExternal.title == key,
                        )
                    )
                    current_externals.pop(key)
        return current_externals


class MPersonExternal(Base):
    __tablename__ = 'person_externals'

    person_id: Mapped[int] = mapped_column(
        sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
        autoincrement=False,
    )
    title: Mapped[str] = mapped_column(sa.String(45), primary_key=True)
    value: Mapped[str | None] = mapped_column(sa.String(45))
