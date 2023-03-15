import sqlalchemy as sa
from datetime import datetime, timezone
from seplis.api.database import auto_session
from seplis.utils.sqlalchemy import UtcDateTime
from .base import Base
from ..dependencies import AsyncSession
from .. import schemas

class Series_watchlist(Base):
    __tablename__ = 'series_watchlist'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(UtcDateTime, nullable=False)


    @auto_session
    async def add(series_id: int, user_id: int | str, session: AsyncSession = None):
        await session.execute(sa.insert(Series_watchlist).values(
            series_id=series_id,
            user_id=user_id,
            created_at=datetime.now(tz=timezone.utc),
        ).prefix_with('IGNORE'))


    @auto_session
    async def remove(series_id: int, user_id: int | str, session: AsyncSession = None):
        await session.execute(sa.delete(Series_watchlist).where(
            Series_watchlist.series_id == series_id,
            Series_watchlist.user_id == user_id,
        ))


    @auto_session
    async def get(series_id: int, user_id: int | str, session: AsyncSession = None):
        f = await session.scalar(sa.select(Series_watchlist.created_at).where(
            Series_watchlist.series_id == series_id,
            Series_watchlist.user_id == user_id,
        ))
        if f:
            return schemas.Series_watchlist(
                on_watchlist=True,
                created_at=f,
            )
        return schemas.Series_watchlist()