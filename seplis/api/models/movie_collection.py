import sqlalchemy as sa
from ...api.database import auto_session, AsyncSession
from .base import Base

class Movie_collection(Base):
    __tablename__ = 'movie_collections'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(200))

    @staticmethod
    @auto_session
    async def get_or_create(name: str, session: AsyncSession = None):
        r = await session.scalar(sa.select(Movie_collection.id).where(Movie_collection.name == name))
        if not r:
            r = await session.execute(sa.insert(Movie_collection).values(name=name))
            r = r.lastrowid
        return r