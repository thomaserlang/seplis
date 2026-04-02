import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from ...api.database import AsyncSession, auto_session
from .base import Base


class MMovieCollection(Base):
    __tablename__ = 'movie_collections'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(sa.String(200))

    @staticmethod
    @auto_session
    async def get_or_create(name: str, session: AsyncSession = None):
        r = await session.scalar(
            sa.select(MMovieCollection.id).where(MMovieCollection.name == name)
        )
        if not r:
            r = await session.execute(sa.insert(MMovieCollection).values(name=name))
            r = r.lastrowid
        return r
