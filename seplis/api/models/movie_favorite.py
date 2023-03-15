import sqlalchemy as sa
from datetime import datetime, timezone
from seplis.utils.sqlalchemy import UtcDateTime
from .base import Base
from ..database import auto_session, AsyncSession


class Movie_favorite(Base):
    __tablename__ = 'movie_favorites'

    movie_id = sa.Column(sa.Integer, sa.ForeignKey(
        'movies.id'), primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(
        'users.id'), primary_key=True, autoincrement=False)
    created_at = sa.Column(UtcDateTime, nullable=False)

    @staticmethod
    @auto_session
    async def add(user_id: int | str, movie_id: int, session: AsyncSession = None):
        await session.execute(sa.insert(Movie_favorite).values(
            movie_id=movie_id,
            user_id=user_id,
            created_at=datetime.now(tz=timezone.utc),
        ).prefix_with('IGNORE'))


    @staticmethod
    @auto_session
    async def remove(user_id: int | str, movie_id: int, session: AsyncSession = None):
        await session.execute(sa.delete(Movie_favorite).where(
            Movie_favorite.movie_id == movie_id,
            Movie_favorite.user_id == user_id,
        ))