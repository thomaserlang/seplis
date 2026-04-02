import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.database import auto_session
from seplis.utils.sqlalchemy import UtcDateTime

from .. import schemas
from ..dependencies import AsyncSession
from .base import Base


class MEpisode(Base):
    __tablename__ = 'episodes'

    series_id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None] = mapped_column(sa.String(200))
    original_title: Mapped[str | None] = mapped_column(sa.String(200))
    air_date: Mapped[date | None] = mapped_column(sa.Date)
    air_datetime: Mapped[datetime | None] = mapped_column(UtcDateTime)
    plot: Mapped[str | None] = mapped_column(sa.String(2000))
    season: Mapped[int | None] = mapped_column()
    episode: Mapped[int | None] = mapped_column()
    runtime: Mapped[int | None] = mapped_column()
    rating: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(4, 2))


class MEpisodeWatchedHistory(Base):
    __tablename__ = 'episodes_watched_history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    series_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade')
    )
    episode_number: Mapped[int | None] = mapped_column()
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade')
    )
    watched_at: Mapped[datetime | None] = mapped_column(UtcDateTime)


class MEpisodeWatched(Base):
    """Episode watched by the user."""

    __tablename__ = 'episodes_watched'

    series_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    episode_number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    times: Mapped[int] = mapped_column(default=0)
    position: Mapped[int] = mapped_column(default=0)
    watched_at: Mapped[datetime] = mapped_column(UtcDateTime)

    @staticmethod
    @auto_session
    async def increment(
        user_id: int,
        series_id: int,
        episode_number: int,
        data: schemas.Episode_watched_increment,
        session: AsyncSession = None,
    ) -> None:
        episode_watched = sa.dialects.mysql.insert(MEpisodeWatched).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=data.watched_at,
            times=1,
        )
        episode_watched = episode_watched.on_duplicate_key_update(
            watched_at=episode_watched.inserted.watched_at,
            times=MEpisodeWatched.times + 1,
            position=0,
        )

        watched_history = sa.insert(MEpisodeWatchedHistory).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=data.watched_at,
        )

        episode_last_watched = (
            sa.dialects.mysql.insert(MEpisodeLastWatched)
            .values(
                series_id=series_id,
                episode_number=episode_number,
                user_id=user_id,
            )
            .on_duplicate_key_update(
                episode_number=episode_number,
            )
        )

        # Including this in the gather makes it not directly avaialble
        # for a select query afterwards
        await session.execute(episode_watched)
        await session.execute(watched_history)
        await session.execute(episode_last_watched)

    @staticmethod
    @auto_session
    async def decrement(
        user_id: int, series_id: int, episode_number: int, session: AsyncSession
    ) -> None:
        w = await session.scalar(
            sa.select(MEpisodeWatched).where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
        )
        if not w:
            return
        if w.times == 0 or (w.times == 1 and w.position == 0):
            await session.execute(
                sa.delete(MEpisodeWatched).where(
                    MEpisodeWatched.series_id == series_id,
                    MEpisodeWatched.episode_number == episode_number,
                    MEpisodeWatched.user_id == user_id,
                )
            )
            await session.execute(
                sa.delete(MEpisodeWatchedHistory).where(
                    MEpisodeWatchedHistory.series_id == series_id,
                    MEpisodeWatchedHistory.episode_number == episode_number,
                    MEpisodeWatchedHistory.user_id == user_id,
                )
            )
        elif w.position > 0:
            watched_at = await session.scalar(
                sa.select(MEpisodeWatchedHistory.watched_at)
                .where(
                    MEpisodeWatchedHistory.series_id == series_id,
                    MEpisodeWatchedHistory.episode_number == episode_number,
                    MEpisodeWatchedHistory.user_id == user_id,
                )
                .order_by(MEpisodeWatchedHistory.watched_at.desc())
                .limit(1)
            )
            await session.execute(
                sa.update(MEpisodeWatched)
                .where(
                    MEpisodeWatched.series_id == series_id,
                    MEpisodeWatched.episode_number == episode_number,
                    MEpisodeWatched.user_id == user_id,
                )
                .values(
                    position=0,
                    watched_at=watched_at,
                )
            )
        else:
            e = await session.execute(
                sa.select(MEpisodeWatchedHistory.id, MEpisodeWatchedHistory.watched_at)
                .where(
                    MEpisodeWatchedHistory.series_id == series_id,
                    MEpisodeWatchedHistory.episode_number == episode_number,
                    MEpisodeWatchedHistory.user_id == user_id,
                )
                .order_by(MEpisodeWatchedHistory.watched_at.desc())
                .limit(2)
            )
            e = e.all()
            await session.execute(
                sa.delete(MEpisodeWatchedHistory).where(
                    MEpisodeWatchedHistory.id == e[0].id,
                )
            )
            await session.execute(
                sa.update(MEpisodeWatched)
                .where(
                    MEpisodeWatched.series_id == series_id,
                    MEpisodeWatched.episode_number == episode_number,
                    MEpisodeWatched.user_id == user_id,
                )
                .values(
                    times=MEpisodeWatched.times - 1,
                    position=0,
                    watched_at=e[1].watched_at,
                )
            )
        await MEpisodeWatched.set_prev_watched(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
        )

    @staticmethod
    @auto_session
    async def set_position(
        user_id, series_id: int, episode_number: int, position: int, session: AsyncSession
    ) -> None:
        if position == 0:
            await MEpisodeWatched.reset_position(
                session=session,
                user_id=user_id,
                series_id=series_id,
                episode_number=episode_number,
            )
            return
        sql = sa.dialects.mysql.insert(MEpisodeWatched).values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
            watched_at=datetime.now(tz=UTC),
            position=position,
        )
        sql = sql.on_duplicate_key_update(
            watched_at=sql.inserted.watched_at,
            position=sql.inserted.position,
        )
        await session.execute(sql)

        sql_watching = (
            sa.dialects.mysql.insert(MEpisodeLastWatched)
            .values(
                series_id=series_id,
                episode_number=episode_number,
                user_id=user_id,
            )
            .on_duplicate_key_update(
                episode_number=episode_number,
            )
        )
        await session.execute(sql_watching)

    @staticmethod
    @auto_session
    async def reset_position(
        user_id: int, series_id: int, episode_number: int, session: AsyncSession
    ) -> None:
        w = await session.scalar(
            sa.select(MEpisodeWatched).where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
        )
        if not w:
            return
        if w.times < 1:
            await asyncio.gather(
                session.execute(
                    sa.delete(MEpisodeWatched).where(
                        MEpisodeWatched.series_id == series_id,
                        MEpisodeWatched.episode_number == episode_number,
                        MEpisodeWatched.user_id == user_id,
                    )
                ),
                session.execute(
                    sa.delete(MEpisodeWatchedHistory).where(
                        MEpisodeWatchedHistory.series_id == series_id,
                        MEpisodeWatchedHistory.episode_number == episode_number,
                        MEpisodeWatchedHistory.user_id == user_id,
                    )
                ),
            )
        else:
            if w.position > 0:
                watched_at = await session.scalar(
                    sa.select(MEpisodeWatchedHistory.watched_at)
                    .where(
                        MEpisodeWatchedHistory.series_id == series_id,
                        MEpisodeWatchedHistory.episode_number == episode_number,
                        MEpisodeWatchedHistory.user_id == user_id,
                    )
                    .order_by(MEpisodeWatchedHistory.watched_at.desc())
                    .limit(1)
                )
                await session.execute(
                    sa.update(MEpisodeWatched)
                    .where(
                        MEpisodeWatched.series_id == series_id,
                        MEpisodeWatched.episode_number == episode_number,
                        MEpisodeWatched.user_id == user_id,
                    )
                    .values(
                        position=0,
                        watched_at=watched_at,
                    )
                )
            else:
                return
        await MEpisodeWatched.set_prev_watched(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
        )

    @staticmethod
    @auto_session
    async def set_prev_watched(
        user_id: int, series_id: int, episode_number: int, session: AsyncSession = None
    ) -> None:
        lew = await session.scalar(
            sa.select(MEpisodeLastWatched).where(
                MEpisodeLastWatched.series_id == series_id,
                MEpisodeLastWatched.user_id == user_id,
            )
        )
        if lew and lew.episode_number == episode_number:
            ep = await session.scalar(
                sa.select(MEpisodeWatchedHistory)
                .where(
                    MEpisodeWatchedHistory.user_id == user_id,
                    MEpisodeWatchedHistory.series_id == series_id,
                )
                .order_by(
                    sa.desc(MEpisodeWatchedHistory.watched_at),
                    sa.desc(MEpisodeWatchedHistory.episode_number),
                )
                .limit(1)
            )
            if not ep:
                await session.execute(
                    sa.delete(MEpisodeLastWatched).where(
                        MEpisodeLastWatched.user_id == user_id,
                        MEpisodeLastWatched.series_id == series_id,
                    )
                )
            else:
                await session.execute(
                    sa.update(MEpisodeLastWatched)
                    .values(
                        episode_number=ep.episode_number,
                    )
                    .where(
                        MEpisodeLastWatched.series_id == series_id,
                        MEpisodeLastWatched.user_id == user_id,
                    )
                )


class MEpisodeLastWatched(Base):
    __tablename__ = 'episode_last_watched'

    series_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    episode_number: Mapped[int | None] = mapped_column()
