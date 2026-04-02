import asyncio

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..database import auto_session
from .base import Base


class MGenre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(sa.String(100))
    type: Mapped[str | None] = mapped_column(sa.String(30))
    number_of: Mapped[int | None] = mapped_column(server_default='0')

    @staticmethod
    @auto_session
    async def get_or_create_genre(genre: str, type_: str, session: AsyncSession = None):
        r = await session.scalar(
            sa.select(MGenre.id).where(
                MGenre.name == genre,
                MGenre.type == type_,
            )
        )
        if not r:
            r = await session.execute(sa.insert(MGenre).values(name=genre, type=type_))
            r = r.lastrowid
        return r

    @staticmethod
    async def get_or_create_genres(genres: list[int | str], type_: str) -> set[int]:
        genre_ids = [genre_id for genre_id in genres if isinstance(genre_id, int)]
        genre_ids.extend(
            await asyncio.gather(
                *[
                    MGenre.get_or_create_genre(genre, type_=type_)
                    for genre in genres
                    if isinstance(genre, str)
                ]
            )
        )
        return set(genre_ids)
