import sqlalchemy as sa
from .base import Base
from ..database import auto_session, AsyncSession
from .. import schemas


class Episode_cast(Base):
    __tablename__ = 'episode_cast'
    person_id = sa.Column(sa.Integer, sa.ForeignKey('people.id'), primary_key=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True)
    person = sa.orm.relationship('Person', lazy=False)
    episode_number = sa.Column(sa.Integer, primary_key=True)
    character = sa.Column(sa.String(200))
    order = sa.Column(sa.Integer)

    @staticmethod
    @auto_session
    async def save(data: schemas.Episode_cast_person_create, session: AsyncSession):
        data_ = data.dict(exclude_unset=True)
        await session.execute(sa.dialects.mysql.insert(Episode_cast).values(
            data_
        ).on_duplicate_key_update(data_))


    @staticmethod
    @auto_session
    async def delete(series_id: int, episode_number: int, person_id: int, session: AsyncSession):
        await session.execute(sa.delete(Episode_cast).where(
            Episode_cast.series_id == series_id,
            Episode_cast.episode_number == episode_number,
            Episode_cast.person_id == person_id,
        ))