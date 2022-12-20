import sqlalchemy as sa
from datetime import datetime, timezone
from .base import Base
from ..dependencies import AsyncSession
from .. import schemas

class Series_follower(Base):
    __tablename__ = 'series_followers'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(sa.DateTime)

    async def follow(series_id: int, user_id: int | str, session: AsyncSession):
        await session.execute(sa.insert(Series_follower).values(
            series_id=series_id,
            user_id=user_id,
            created_at=datetime.now(tz=timezone.utc),
        ).prefix_with('IGNORE'))

    async def unfollow(series_id: int, user_id: int | str, session: AsyncSession):
        await session.execute(sa.delete(Series_follower).where(
            Series_follower.series_id == series_id,
            Series_follower.user_id == user_id,
        ))

    async def get(series_id: int, user_id: int | str, session: AsyncSession):
        f = await session.scalar(sa.select(Series_follower.created_at).where(
            Series_follower.series_id == series_id,
            Series_follower.user_id == user_id,
        ))
        if f:
            return schemas.Series_following(
                following=True,
                created_at=f,
            )
        return schemas.Series_following()