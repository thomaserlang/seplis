from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.database import auto_session
from seplis.utils.sqlalchemy import UtcDateTime

from .. import schemas
from ..dependencies import AsyncSession
from .base import Base


class MSeriesFavorite(Base):
    __tablename__ = 'series_favorites'

    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id'), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey('users.id'), primary_key=True, autoincrement=False
    )
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)

    @auto_session
    async def add(
        series_id: int, user_id: int | str, session: AsyncSession = None
    ) -> None:
        await session.execute(
            sa.insert(MSeriesFavorite)
            .values(
                series_id=series_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
            .prefix_with('IGNORE')
        )

    @auto_session
    async def remove(
        series_id: int, user_id: int | str, session: AsyncSession = None
    ) -> None:
        await session.execute(
            sa.delete(MSeriesFavorite).where(
                MSeriesFavorite.series_id == series_id,
                MSeriesFavorite.user_id == user_id,
            )
        )

    @auto_session
    async def get(series_id: int, user_id: int | str, session: AsyncSession = None):
        f = await session.scalar(
            sa.select(MSeriesFavorite.created_at).where(
                MSeriesFavorite.series_id == series_id,
                MSeriesFavorite.user_id == user_id,
            )
        )
        if f:
            return schemas.Series_favorite(
                favorite=True,
                created_at=f,
            )
        return schemas.Series_favorite()
