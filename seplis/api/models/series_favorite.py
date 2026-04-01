from datetime import UTC, datetime

import sqlalchemy as sa

from seplis.api.database import auto_session
from seplis.utils.sqlalchemy import UtcDateTime

from .. import schemas
from ..dependencies import AsyncSession
from .base import Base


class Series_favorite(Base):
    __tablename__ = 'series_favorites'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(UtcDateTime, nullable=False)


    @auto_session
    async def add(series_id: int, user_id: int | str, session: AsyncSession = None) -> None:
        await session.execute(sa.insert(Series_favorite).values(
            series_id=series_id,
            user_id=user_id,
            created_at=datetime.now(tz=UTC),
        ).prefix_with('IGNORE'))


    @auto_session
    async def remove(series_id: int, user_id: int | str, session: AsyncSession = None) -> None:
        await session.execute(sa.delete(Series_favorite).where(
            Series_favorite.series_id == series_id,
            Series_favorite.user_id == user_id,
        ))


    @auto_session
    async def get(series_id: int, user_id: int | str, session: AsyncSession = None):
        f = await session.scalar(sa.select(Series_favorite.created_at).where(
            Series_favorite.series_id == series_id,
            Series_favorite.user_id == user_id,
        ))
        if f:
            return schemas.Series_favorite(
                favorite=True,
                created_at=f,
            )
        return schemas.Series_favorite()