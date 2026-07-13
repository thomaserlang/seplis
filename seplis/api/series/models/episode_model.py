from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime

from ..schemas.episode_schemas import Episode, EpisodeWatched


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


class MEpisodeLastWatched(Base):
    __tablename__ = 'episode_last_watched'

    series_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    episode_number: Mapped[int | None] = mapped_column()


def episode_mapper(episode: MEpisode) -> Episode:
    return Episode(
        number=episode.number,
        title=episode.title,
        original_title=episode.original_title,
        season=episode.season,
        episode=episode.episode,
        air_date=episode.air_date,
        air_datetime=episode.air_datetime,
        plot=episode.plot,
        runtime=episode.runtime,
        rating=float(episode.rating) if episode.rating is not None else None,
    )


def episode_watched_mapper(watched: MEpisodeWatched) -> EpisodeWatched:
    return EpisodeWatched(
        episode_number=watched.episode_number,
        times=watched.times or 0,
        position=watched.position or 0,
        watched_at=watched.watched_at,
    )
