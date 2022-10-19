import asyncio
import sqlalchemy as sa
from datetime import datetime, timezone
from .base import Base
from ..dependencies import AsyncSession
from .. import schemas
from ... import logger


class Episode(Base):
    __tablename__ = 'episodes'

    show_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(200), unique=True)
    air_date = sa.Column(sa.Date)
    air_time = sa.Column(sa.Time)
    air_datetime = sa.Column(sa.DateTime)
    description_text = sa.Column(sa.Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    season = sa.Column(sa.Integer)
    episode = sa.Column(sa.Integer)
    runtime = sa.Column(sa.Integer)

    @property
    def description(self):
        return {
            'text': self.description_text,
            'title': self.description_title,
            'url': self.description_url,
        }


class Episode_watched_history(Base):
    __tablename__ = 'episodes_watched_history'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    series_id = sa.Column(sa.Integer, sa.ForeignKey('shows.id', onupdate='cascade', ondelete='cascade'), primary_key=False, autoincrement=False)
    episode_number = sa.Column(sa.Integer)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), primary_key=False, autoincrement=False)
    watched_at = sa.Column(sa.DateTime)


class Episode_watched(Base):
    """Episode watched by the user."""
    __tablename__ = 'episodes_watched'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    times = sa.Column(sa.Integer, default=0)
    position = sa.Column(sa.Integer, default=0)
    watched_at = sa.Column(sa.DateTime)

    @staticmethod
    async def increment(session: AsyncSession, user_id: int, series_id: int, episode_number: int, data: schemas.Episode_watched_increment):
        sql = sa.dialects.mysql.insert(Episode_watched).values(
            show_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=data.watched_at,
            times=1
        )
        sql = sql.on_duplicate_key_update(
            watched_at=sql.inserted.watched_at,
            times=Episode_watched.times + 1,
            position=0,
        )
        sql_history = sa.insert(Episode_watched_history).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=data.watched_at,
        )
        sql_watching = sa.dialects.mysql.insert(Episode_watching).values(
            show_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
        ).on_duplicate_key_update(
            episode_number=episode_number,
        )
        await asyncio.gather(
            session.execute(sql),
            session.execute(sql_history),
            session.execute(sql_watching),
        )


    @staticmethod
    async def decrement(session: AsyncSession, user_id: int, series_id: int, episode_number: int):
        w = await session.scalar(sa.select(Episode_watched).where(
            Episode_watched.show_id == series_id,
            Episode_watched.episode_number == episode_number,
            Episode_watched.user_id == user_id,
        ))
        if not w:
            return
        if w.times <= 1:
            await asyncio.gather(
                session.execute(sa.delete(Episode_watched).where(
                    Episode_watched.show_id == series_id,
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
            watched_at = await session.scalar(sa.select(Episode_watched_history.watched_at).where(
                Episode_watched_history.series_id == series_id,
                Episode_watched_history.episode_number == episode_number,
                Episode_watched_history.user_id == user_id,
            ).order_by(
                Episode_watched_history.watched_at.desc()
            ).limit(1))
            if w.position > 0:
                await session.execute(sa.update(Episode_watched).where(
                    Episode_watched.show_id == series_id,
                    Episode_watched.episode_number == episode_number,
                    Episode_watched.user_id == user_id,
                ).values(
                    position=0,
                    watched_at=watched_at,
                ))
            else:
                id_ = await session.scalar(sa.select(Episode_watched_history.id).where(
                    Episode_watched_history.series_id == series_id,
                    Episode_watched_history.episode_number == episode_number,
                    Episode_watched_history.user_id == user_id,
                ).order_by(
                    Episode_watched_history.watched_at.desc()
                ).limit(1))
                await asyncio.gather(
                    session.execute(sa.update(Episode_watched).where(
                        Episode_watched.show_id == series_id,
                        Episode_watched.episode_number == episode_number,
                        Episode_watched.user_id == user_id,
                    ).values(
                        times=Episode_watched.times - 1,
                        position=0,
                        watched_at=watched_at,
                    )),
                    session.execute(sa.delete(Episode_watched_history).where(
                        Episode_watched_history.id == id_,
                    ))
                )
        await Episode_watched.set_prev_watched(session=session, user_id=user_id, series_id=series_id, episode_number=episode_number)


    @staticmethod
    async def set_position(session: AsyncSession, user_id, series_id: int, episode_number: int, position: int):
        if position == 0:
            await Episode_watched.reset_position(session=session, user_id=user_id, series_id=series_id, episode_number=episode_number)
            return
        sql = sa.dialects.mysql.insert(Episode_watched).values(
            show_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=datetime.now(tz=timezone.utc),
            position=position,
        )
        sql = sql.on_duplicate_key_update(
            watched_at=sql.inserted.watched_at,
            position=sql.inserted.position,
        )
        sql_watching = sa.dialects.mysql.insert(Episode_watching).values(
            show_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
        ).on_duplicate_key_update(
            episode_number=episode_number,
        )
        await asyncio.gather(
            session.execute(sql),
            session.execute(sql_watching),
        )


    @staticmethod
    async def reset_position(session: AsyncSession, user_id: int, series_id: int, episode_number: int):
        w = await session.scalar(sa.select(Episode_watched).where(
            Episode_watched.show_id == series_id,
            Episode_watched.episode_number == episode_number,
            Episode_watched.user_id == user_id,
        ))
        if not w:
            return
        if w.times < 1:
            await asyncio.gather(
                session.execute(sa.delete(Episode_watched).where(
                    Episode_watched.show_id == series_id,
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
                    Episode_watched.show_id == series_id,
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
    async def set_prev_watched(session: AsyncSession, user_id: int, series_id:int, episode_number: int):
        lew = await session.scalar(sa.select(Episode_watching).where(
            Episode_watching.show_id == series_id,
            Episode_watching.user_id == user_id,
        ))
        if lew and lew.episode_number == episode_number:
            ep = await session.scalar(sa.select(Episode_watched_history).where(
                Episode_watched_history.user_id == user_id,
                Episode_watched_history.series_id == series_id,
                Episode_watched_history.episode_number != episode_number
            ).order_by(
                sa.desc(Episode_watched_history.watched_at),
                sa.desc(Episode_watched_history.episode_number),
            ).limit(1))
            if not ep:
                await session.execute(sa.delete(Episode_watching).where(
                    Episode_watching.user_id == user_id,
                    Episode_watching.show_id == series_id,
                ))
            else:
                await session.execute(sa.update(Episode_watching).values(
                    episode_number=ep.episode_number,
                ).where(
                    Episode_watching.show_id == series_id,
                    Episode_watching.user_id == user_id,
                ))


class Episode_watching(Base):
    __tablename__ = 'episode_watching'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer)