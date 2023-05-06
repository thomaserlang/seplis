import sqlalchemy as sa
from datetime import datetime, timezone

from ..database import auto_session, AsyncSession
from .base import Base
from .. import schemas, exceptions
from ... import utils


class Person(Base):
    __tablename__ = 'people'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    created_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.DateTime)
    name = sa.Column(sa.String(500), nullable=False)
    also_known_as = sa.Column(sa.JSON, nullable=False)
    gender = sa.Column(sa.SMALLINT)
    birthday = sa.Column(sa.Date)
    deathday = sa.Column(sa.Date)
    biography = sa.Column(sa.String(2000))
    place_of_birth = sa.Column(sa.String(100))
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4))
    externals = sa.Column(sa.JSON, nullable=False)
    profile_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id', onupdate='cascade', ondelete='set null'))
    profile_image = sa.orm.relationship('Image', lazy=False)

    @classmethod
    @auto_session
    async def save(cls, 
        data,
        person_id: int = None, 
        patch: bool = True,
        session: AsyncSession = None,
    ):
        _data = data.dict(exclude_unset=True)
        if not person_id:
            _data['created_at'] = datetime.now(tz=timezone.utc)
            r = await session.execute(sa.insert(Person))
            person_id = r.lastrowid
        else:
            _data['updated_at'] = datetime.now(tz=timezone.utc)

        if 'externals' in _data:
            _data['externals'] = await cls._save_externals(session, person_id, _data['externals'], patch)

        if _data:
            await session.execute(sa.update(Person).where(Person.id == person_id).values(_data))

        person = await session.scalar(sa.select(Person).where(Person.id == person_id))
        return schemas.Person.from_orm(person)
    
    @staticmethod
    @auto_session
    async def delete(person_id: int, session: AsyncSession = None):
        await session.execute(sa.delete(Person).where(Person.id == person_id))
    
    @staticmethod
    @auto_session
    async def get_from_external(
        title: str,
        value: str,
        session: AsyncSession = None,
    ):
        person = await session.scalar(sa.select(Person).where(
            Person.id == Person_external.person_id,
            Person_external.title == title,
            Person_external.value == value,
        ))
        if person:
            return schemas.Person.from_orm(person)
        
    @staticmethod
    @auto_session
    async def get(person_id: int, session: AsyncSession = None):
        person = await session.scalar(sa.select(Person).where(Person.id == person_id))
        if person:
            return schemas.Person.from_orm(person)

    @staticmethod
    async def _save_externals(session: AsyncSession, person_id: str | int, externals: dict[str, str | None], patch: bool):
        current_externals = {}
        if not patch:
            await session.execute(sa.delete(Person_external).where(Person_external.person_id == person_id))
        else:
            current_externals = await session.scalar(sa.select(Person.externals).where(Person.id == person_id))
        for key in externals:
            if externals[key]:
                r = await session.scalar(sa.select(Person).where(
                    Person_external.title == key,
                    Person_external.value == externals[key],
                    Person_external.person_id != person_id,
                    Person.id == Person_external.person_id,
                ))
                if r:
                    raise exceptions.Person_external_duplicated(
                        external_title=key,
                        external_value=externals[key],
                        person=utils.json_loads(utils.json_dumps(
                            schemas.Person.from_orm(r)))
                    )
            
            if (key not in current_externals):
                if externals[key]:
                    await session.execute(sa.insert(Person_external)
                                          .values(person_id=person_id, title=key, value=externals[key]))
                    current_externals[key] = externals[key]
            elif (current_externals[key] != externals[key]):
                if (externals[key]):
                    await session.execute(sa.update(Person_external).where(
                        Person_external.person_id == person_id,
                        Person_external.title == key,
                    ).values(value=externals[key]))
                    current_externals[key] = externals[key]
                else:
                    await session.execute(sa.delete(Person_external).where(
                        Person_external.person_id == person_id,
                        Person_external.title == key
                    ))
                    current_externals.pop(key)
        return current_externals
    
    
class Person_external(Base):
    __tablename__ = 'person_externals'
    
    person_id = sa.Column(sa.Integer, sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))