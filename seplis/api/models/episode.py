import asyncio
import sqlalchemy as sa
from datetime import datetime, timezone
from seplis.api.database import auto_session
from seplis.utils.sqlalchemy import UtcDateTime
from .base import Base
from ..dependencies import AsyncSession
from .. import schemas
from ... import logger


class Episode(Base):
    __tablename__ = 'episodes'

    series_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(200))
    original_title = sa.Column(sa.String(200))
    air_date = sa.Column(sa.Date)
    air_datetime = sa.Column(UtcDateTime)
    plot = sa.Column(sa.String(2000))
    season = sa.Column(sa.Integer)
    episode = sa.Column(sa.Integer)
    runtime = sa.Column(sa.Integer)
    rating = sa.Column(sa.DECIMAL(4, 2))


class Episode_watched_history(Base):
    __tablename__ = 'episodes_watched_history'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=False, autoincrement=False)
    episode_number = sa.Column(sa.Integer)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), primary_key=False, autoincrement=False)
    watched_at = sa.Column(UtcDateTime)


class Episode_watched(Base):
    """Episode watched by the user."""
    __tablename__ = 'episodes_watched'

    series_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    times = sa.Column(sa.Integer, default=0, nullable=False)
    position = sa.Column(sa.Integer, default=0, nullable=False)
    watched_at = sa.Column(UtcDateTime, nullable=False)

    @staticmethod
    @auto_session
    async def increment(user_id: int, series_id: int, episode_number: int, data: schemas.Episode_watched_increment, session: AsyncSession=None):
        episode_watched = sa.dialects.mysql.insert(Episode_watched).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=data.watched_at,
            times=1
        )
        episode_watched = episode_watched.on_duplicate_key_update(
            watched_at=episode_watched.inserted.watched_at,
            times=Episode_watched.times + 1,
            position=0,
        )

        watched_history = sa.insert(Episode_watched_history).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=data.watched_at,
        )

        episode_last_watched = sa.dialects.mysql.insert(Episode_last_watched).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
        ).on_duplicate_key_update(
            episode_number=episode_number,
        )
        
        # Including this in the gather makes it not directly avaialble 
        # for a select query afterwards
        await session.execute(episode_watched) 
        await session.execute(watched_history)
        await session.execute(episode_last_watched)


    @staticmethod
    @auto_session
    async def decrement(user_id: int, series_id: int, episode_number: int, session: AsyncSession):
        w = await session.scalar(sa.select(Episode_watched).where(
            Episode_watched.series_id == series_id,
            Episode_watched.episode_number == episode_number,
            Episode_watched.user_id == user_id,
        ))
        if not w:
            return
        if w.times == 0 or (w.times == 1 and w.position == 0):
            await session.execute(sa.delete(Episode_watched).where(
                Episode_watched.series_id == series_id,
                Episode_watched.episode_number == episode_number,
                Episode_watched.user_id == user_id,
            ))
            await session.execute(sa.delete(Episode_watched_history).where(
                Episode_watched_history.series_id == series_id,
                Episode_watched_history.episode_number == episode_number,
                Episode_watched_history.user_id == user_id,
            ))
        elif w.position > 0:
            watched_at = await session.scalar(sa.select(Episode_watched_history.watched_at).where(
                Episode_watched_history.series_id == series_id,
                Episode_watched_history.episode_number == episode_number,
                Episode_watched_history.user_id == user_id,
            ).order_by(
                Episode_watched_history.watched_at.desc()
            ).limit(1))
            await session.execute(sa.update(Episode_watched).where(
                Episode_watched.series_id == series_id,
                Episode_watched.episode_number == episode_number,
                Episode_watched.user_id == user_id,
            ).values(
                position=0,
                watched_at=watched_at,
            ))
        else:
            e = await session.execute(sa.select(Episode_watched_history.id, Episode_watched_history.watched_at).where(
                Episode_watched_history.series_id == series_id,
                Episode_watched_history.episode_number == episode_number,
                Episode_watched_history.user_id == user_id,
            ).order_by(
                Episode_watched_history.watched_at.desc()
            ).limit(2))
            e = e.all()
            await session.execute(sa.delete(Episode_watched_history).where(
                Episode_watched_history.id == e[0].id,
            ))
            await session.execute(sa.update(Episode_watched).where(
                Episode_watched.series_id == series_id,
                Episode_watched.episode_number == episode_number,
                Episode_watched.user_id == user_id,
            ).values(
                times=Episode_watched.times - 1,
                position=0,
                watched_at=e[1].watched_at,
            ))
        await Episode_watched.set_prev_watched(session=session, user_id=user_id, series_id=series_id, episode_number=episode_number)


    @staticmethod
    @auto_session
    async def set_position(user_id, series_id: int, episode_number: int, position: int, session: AsyncSession):
        if position == 0:
            await Episode_watched.reset_position(session=session, user_id=user_id, series_id=series_id, episode_number=episode_number)
            return
        sql = sa.dialects.mysql.insert(Episode_watched).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=datetime.now(tz=timezone.utc),
            position=position,
        )
        sql = sql.on_duplicate_key_update(
            watched_at=sql.inserted.watched_at,
            position=sql.inserted.position,
        )
        await session.execute(sql)

        sql_watching = sa.dialects.mysql.insert(Episode_last_watched).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
        ).on_duplicate_key_update(
            episode_number=episode_number,
        )
        await session.execute(sql_watching)


    @staticmethod
    @auto_session
    async def reset_position(user_id: int, series_id: int, episode_number: int, session: AsyncSession):
        w = await session.scalar(sa.select(Episode_watched).where(
            Episode_watched.series_id == series_id,
            Episode_watched.episode_number == episode_number,
            Episode_watched.user_id == user_id,
        ))
        if not w:
            return
        if w.times < 1:
            await asyncio.gather(
                session.execute(sa.delete(Episode_watched).where(
                    Episode_watched.series_id == series_id,
                    Episode_watched.episode_number == episode_number,
                    Episode_watched.user_id == user_id,
                )),
                session.execute(sa.delete(Episode_watched_history).where(
                    Episode_watched_history.series_id == series_id,
                    Episode_watched_history.episode_number == episode_number,
                    Episode_watched_history.user_id == user_id,
                )),
            )
        else:
            if w.position > 0:
                watched_at = await session.scalar(sa.select(Episode_watched_history.watched_at).where(
                    Episode_watched_history.series_id == series_id,
                    Episode_watched_history.episode_number == episode_number,
                    Episode_watched_history.user_id == user_id,
                ).order_by(
                    Episode_watched_history.watched_at.desc()
                ).limit(1))
                await session.execute(sa.update(Episode_watched).where(
                    Episode_watched.series_id == series_id,
                    Episode_watched.episode_number == episode_number,
                    Episode_watched.user_id == user_id,
                ).values(
                    position=0,
                    watched_at=watched_at,
                ))
            else:
                return
        await Episode_watched.set_prev_watched(session=session, user_id=user_id, series_id=series_id, episode_number=episode_number)


    @staticmethod
    @auto_session
    async def set_prev_watched(user_id: int, series_id:int, episode_number: int, session: AsyncSession = None):
        lew = await session.scalar(sa.select(Episode_last_watched).where(
            Episode_last_watched.series_id == series_id,
            Episode_last_watched.user_id == user_id,
        ))
        if lew and lew.episode_number == episode_number:
            ep = await session.scalar(sa.select(Episode_watched_history).where(
                Episode_watched_history.user_id == user_id,
                Episode_watched_history.series_id == series_id,
            ).order_by(
                sa.desc(Episode_watched_history.watched_at),
                sa.desc(Episode_watched_history.episode_number),
            ).limit(1))
            if not ep:
                await session.execute(sa.delete(Episode_last_watched).where(
                    Episode_last_watched.user_id == user_id,
                    Episode_last_watched.series_id == series_id,
                ))
            else:
                await session.execute(sa.update(Episode_last_watched).values(
                    episode_number=ep.episode_number,
                ).where(
                    Episode_last_watched.series_id == series_id,
                    Episode_last_watched.user_id == user_id,
                ))


class Episode_last_watched(Base):
    __tablename__ = 'episode_last_watched'

    series_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer)