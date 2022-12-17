import sqlalchemy as sa
from .base import Base
from sqlalchemy.ext.asyncio import AsyncSession

class Genre(Base):
    __tablename__ = 'genres'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100))

    @staticmethod
    async def get_or_create_genre(session: AsyncSession, genre: str):
        r = await session.scalar(sa.select(Genre.id).where(Genre.name == genre))
        if not r:
            r = await session.execute(sa.insert(Genre).values(name=genre))
            r = r.lastrowid
        return r