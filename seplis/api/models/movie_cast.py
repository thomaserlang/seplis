import sqlalchemy as sa
from .base import Base
from ..database import auto_session, AsyncSession
from .. import schemas


class Movie_cast(Base):
    __tablename__ = 'movie_cast'
    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id'), primary_key=True)
    person_id = sa.Column(sa.Integer, sa.ForeignKey('people.id'), primary_key=True)
    person = sa.orm.relationship('Person', lazy=False)
    character = sa.Column(sa.String(200))
    order = sa.Column(sa.Integer)

    @staticmethod
    @auto_session
    async def save(data: schemas.Movie_cast_person_create, session: AsyncSession):
        data_ = data.dict(exclude_unset=True)
        await session.execute(sa.dialects.mysql.insert(Movie_cast).values(
            data_
        ).on_duplicate_key_update(data_))

    @staticmethod
    @auto_session
    async def delete(movie_id: int, person_id: int, session: AsyncSession):
        await session.execute(sa.delete(Movie_cast).where(
            Movie_cast.movie_id == movie_id,
            Movie_cast.person_id == person_id,
        ))