import sqlalchemy as sa
from seplis.api.database import auto_session, AsyncSession
from .base import Base
from .. import schemas

class Series_cast(Base):
    __tablename__ = 'series_cast'
    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True)
    person_id = sa.Column(sa.Integer, sa.ForeignKey('people.id'), primary_key=True)
    person = sa.orm.relationship('Person', lazy=False)
    character = sa.Column(sa.String(200))
    order = sa.Column(sa.Integer)
    total_episodes = sa.Column(sa.Integer)

    @staticmethod
    @auto_session
    async def save(data: schemas.Series_cast_person_create, session: AsyncSession):
        data_ = data.dict(exclude_unset=True)
        await session.execute(sa.dialects.mysql.insert(Series_cast).values(
            data_
        ).on_duplicate_key_update(data_))

    @staticmethod
    @auto_session
    async def delete(series_id: int, person_id: int, session: AsyncSession):
        await session.execute(sa.delete(Series_cast).where(
            Series_cast.series_id == series_id,
            Series_cast.person_id == person_id,
        ))