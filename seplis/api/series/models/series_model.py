from datetime import date, datetime
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seplis import constants
from seplis.api.genre import Genre, genre_mapper
from seplis.api.image import image_mapper
from seplis.api.image.models.image_model import MImage
from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime

from ..schemas.series_schemas import (
    Series,
    SeriesImporters,
    SeriesSeason,
)


class MSeries(Base):
    __tablename__ = 'series'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime | None] = mapped_column(UtcDateTime)
    status: Mapped[int] = mapped_column(default=0)
    title: Mapped[str | None] = mapped_column(sa.String(200))
    original_title: Mapped[str | None] = mapped_column(sa.String(200))
    plot: Mapped[str | None] = mapped_column(sa.String(2000))
    tagline: Mapped[str | None] = mapped_column(sa.String(500))
    premiered: Mapped[date | None] = mapped_column(sa.Date)
    ended: Mapped[date | None] = mapped_column(sa.Date)
    externals: Mapped[dict | None] = mapped_column(sa.JSON(), default=lambda: {})
    importer_info: Mapped[str | None] = mapped_column(sa.String(45))
    importer_episodes: Mapped[str | None] = mapped_column(sa.String(45))
    seasons: Mapped[list | None] = mapped_column(sa.JSON(), default=lambda: [])
    runtime: Mapped[int | None] = mapped_column()
    genres: Mapped[list | None] = mapped_column(sa.JSON(), default=lambda: [])
    alternative_titles: Mapped[list | None] = mapped_column(sa.JSON(), default=lambda: [])
    poster_image_id: Mapped[int | None] = mapped_column(sa.ForeignKey('images.id'))
    poster_image: Mapped[MImage | None] = relationship('MImage', lazy=False)
    episode_type: Mapped[int | None] = mapped_column(
        default=constants.SHOW_EPISODE_TYPE_SEASON_EPISODE
    )
    total_episodes: Mapped[int | None] = mapped_column(default=0)
    language: Mapped[str | None] = mapped_column(sa.String(100))
    popularity: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(precision=12, scale=4))
    rating: Mapped[Decimal | None] = mapped_column(sa.DECIMAL(4, 2))
    rating_votes: Mapped[int | None] = mapped_column()
    rating_weighted: Mapped[Decimal] = mapped_column(
        sa.DECIMAL(precision=12, scale=4), server_default='0'
    )

    @property
    def importers(self) -> dict[str, str | None]:
        return {
            'info': self.importer_info,
            'episodes': self.importer_episodes,
        }


class MSeriesExternal(Base):
    __tablename__ = 'series_externals'

    series_id: Mapped[int] = mapped_column(sa.ForeignKey('series.id'), primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(45), primary_key=True)
    value: Mapped[str | None] = mapped_column(sa.String(45))


class MSeriesGenre(Base):
    __tablename__ = 'series_genres'

    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id'), primary_key=True, autoincrement=False
    )
    genre_id: Mapped[int] = mapped_column(
        sa.ForeignKey('genres.id', ondelete='cascade', onupdate='cascade'),
        primary_key=True,
        autoincrement=False,
    )


def series_season_from_value(value: Any) -> SeriesSeason:
    if isinstance(value, SeriesSeason):
        return value
    return SeriesSeason(
        season=int(value.get('season') or 0),
        from_=int(value.get('from_') or value.get('from') or 0),
        to=int(value.get('to') or 0),
        total=int(value.get('total') or 0),
    )


def genre_from_value(value: Any) -> Genre:
    if isinstance(value, Genre):
        return value
    if isinstance(value, dict):
        return Genre(
            id=int(value.get('id') or 0),
            name=str(value.get('name') or ''),
            number_of=int(value.get('number_of') or 0),
        )
    return genre_mapper(value)


def genres_from_values(values: list[Any] | None) -> list[Genre]:
    return [genre_from_value(value) for value in values or []]


def series_mapper(series: MSeries) -> Series:
    return Series(
        id=series.id,
        title=series.title,
        original_title=series.original_title,
        alternative_titles=list(series.alternative_titles or []),
        externals=dict(series.externals or {}),
        plot=series.plot,
        tagline=series.tagline,
        premiered=series.premiered,
        ended=series.ended,
        importers=SeriesImporters(
            info=series.importer_info,
            episodes=series.importer_episodes,
        ),
        runtime=series.runtime,
        genres=genres_from_values(series.genres),
        episode_type=series.episode_type,
        language=series.language,
        created_at=series.created_at,
        updated_at=series.updated_at,
        status=series.status,
        seasons=[series_season_from_value(value) for value in series.seasons or []],
        total_episodes=series.total_episodes or 0,
        poster_image=image_mapper(series.poster_image) if series.poster_image else None,
        popularity=float(series.popularity) if series.popularity is not None else None,
        rating=float(series.rating) if series.rating is not None else None,
        rating_votes=series.rating_votes,
    )
