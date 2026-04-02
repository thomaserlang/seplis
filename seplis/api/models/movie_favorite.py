from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.utils.sqlalchemy import UtcDateTime

from ..database import AsyncSession, auto_session
from .base import Base


class MMovieFavorite(Base):
    __tablename__ = 'movie_favorites'

    movie_id: Mapped[int] = mapped_column(
        sa.ForeignKey('movies.id'), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey('users.id'), primary_key=True, autoincrement=False
    )
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)

    @staticmethod
    @auto_session
    async def add(
        user_id: int | str, movie_id: int, session: AsyncSession = None
    ) -> None:
        await session.execute(
            sa.insert(MMovieFavorite)
            .values(
                movie_id=movie_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
            .prefix_with('IGNORE')
        )

    @staticmethod
    @auto_session
    async def remove(
        user_id: int | str, movie_id: int, session: AsyncSession = None
    ) -> None:
        await session.execute(
            sa.delete(MMovieFavorite).where(
                MMovieFavorite.movie_id == movie_id,
                MMovieFavorite.user_id == user_id,
            )
        )
