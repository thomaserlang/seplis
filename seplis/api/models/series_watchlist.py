from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.database import auto_session
from seplis.utils.sqlalchemy import UtcDateTime

from .. import schemas
from ..dependencies import AsyncSession
from .base import Base


class MSeriesWatchlist(Base):
    __tablename__ = 'series_watchlist'

    series_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('series.id'), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False
    )
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)

    @auto_session
    async def add(
        series_id: int, user_id: int | str, session: AsyncSession = None
    ) -> None:
        await session.execute(
            sa.insert(MSeriesWatchlist)
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
            sa.delete(MSeriesWatchlist).where(
                MSeriesWatchlist.series_id == series_id,
                MSeriesWatchlist.user_id == user_id,
            )
        )

    @auto_session
    async def get(series_id: int, user_id: int | str, session: AsyncSession = None):
        f = await session.scalar(
            sa.select(MSeriesWatchlist.created_at).where(
                MSeriesWatchlist.series_id == series_id,
                MSeriesWatchlist.user_id == user_id,
            )
        )
        if f:
            return schemas.Series_watchlist(
                on_watchlist=True,
                created_at=f,
            )
        return schemas.Series_watchlist()
