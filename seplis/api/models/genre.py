import sqlalchemy as sa
import asyncio

from ..database import auto_session
from .base import Base
from sqlalchemy.ext.asyncio import AsyncSession

class Genre(Base):
    __tablename__ = 'genres'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100))
    type = sa.Column(sa.String(30))
    number_of = sa.Column(sa.Integer, server_default='0')

    @staticmethod
    @auto_session
    async def get_or_create_genre(genre: str, type_: str, session: AsyncSession = None):
        r = await session.scalar(sa.select(Genre.id).where(
            Genre.name == genre, 
            Genre.type == type_,
        ))
        if not r:
            r = await session.execute(sa.insert(Genre).values(name=genre, type=type_))
            r = r.lastrowid
        return r

    @staticmethod
    async def get_or_create_genres(genres: list[int | str], type_: str) -> set[int]:
        genre_ids = [genre_id for genre_id in genres if isinstance(genre_id, int)]
        genre_ids.extend(await asyncio.gather(*[Genre.get_or_create_genre(genre, type_=type_) \
            for genre in genres if isinstance(genre, str)]))
        return set(genre_ids)