import sqlalchemy as sa
from datetime import datetime, timezone
from .base import Base
from ..dependencies import AsyncSession
from .. import schemas

class Series_following(Base):
    __tablename__ = 'show_fans'

    show_id = sa.Column(sa.Integer, sa.ForeignKey('shows.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(sa.DateTime)

    async def follow(series_id: int, user_id: int | str, session: AsyncSession):
        await session.execute(sa.insert(Series_following).values(
            show_id=series_id,
            user_id=user_id,
            created_at=datetime.now(tz=timezone.utc),
        ).prefix_with('IGNORE'))

    async def unfollow(series_id: int, user_id: int | str, session: AsyncSession):
        await session.execute(sa.delete(Series_following).where(
            Series_following.show_id == series_id,
            Series_following.user_id == user_id,
        ))

    async def get(series_id: int, user_id: int | str, session: AsyncSession):
        f = await session.scalar(sa.select(Series_following.created_at).where(
            Series_following.show_id == series_id,
            Series_following.user_id == user_id,
        ))
        if f:
            return schemas.Series_following(
                following=True,
                created_at=f,
            )
        return schemas.Series_following()