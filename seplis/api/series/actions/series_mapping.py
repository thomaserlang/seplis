from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.genre import Genre
from seplis.api.image import image_columns, image_mapper
from seplis.api.image.models.image_model import MImage

from ..models.episode_model import MEpisode
from ..models.series_model import MSeries
from ..schemas.episode_schemas import Episode, EpisodeWatched
from ..schemas.series_schemas import Series, SeriesImporters, SeriesSeason


def episode_columns(prefix: str = 'episode_') -> tuple[Any, ...]:
    return tuple(
        column.label(f'{prefix}{column.name}') for column in MEpisode.__table__.columns
    )


def select_series() -> sa.Select[Any]:
    return sa.select(MSeries.__table__, *image_columns()).outerjoin(
        MImage.__table__, MImage.id == MSeries.poster_image_id
    )


def series_row_mapper(series: RowMapping) -> Series:
    popularity = series['popularity']
    rating = series['rating']
    return Series(
        id=series['id'],
        title=series['title'],
        original_title=series['original_title'],
        alternative_titles=list(series['alternative_titles'] or []),
        externals=dict(series['externals'] or {}),
        plot=series['plot'],
        tagline=series['tagline'],
        premiered=series['premiered'],
        ended=series['ended'],
        importers=SeriesImporters(
            info=series['importer_info'],
            episodes=series['importer_episodes'],
        ),
        runtime=series['runtime'],
        genres=[
            value
            if isinstance(value, Genre)
            else Genre(
                id=int(value.get('id') or 0),
                name=str(value.get('name') or ''),
                number_of=int(value.get('number_of') or 0),
            )
            for value in series['genres'] or []
        ],
        episode_type=series['episode_type'],
        language=series['language'],
        created_at=series['created_at'],
        updated_at=series['updated_at'],
        status=series['status'],
        seasons=[
            value
            if isinstance(value, SeriesSeason)
            else SeriesSeason(
                season=int(value.get('season') or 0),
                from_=int(value.get('from_') or value.get('from') or 0),
                to=int(value.get('to') or 0),
                total=int(value.get('total') or 0),
            )
            for value in series['seasons'] or []
        ],
        total_episodes=series['total_episodes'] or 0,
        poster_image=image_mapper(series, 'image_') if series['image_id'] else None,
        popularity=float(popularity) if popularity is not None else None,
        rating=float(rating) if rating is not None else None,
        rating_votes=series['rating_votes'],
    )


def episode_row_mapper(episode: RowMapping, prefix: str = '') -> Episode:
    rating = episode[f'{prefix}rating']
    return Episode(
        number=episode[f'{prefix}number'],
        title=episode[f'{prefix}title'],
        original_title=episode[f'{prefix}original_title'],
        season=episode[f'{prefix}season'],
        episode=episode[f'{prefix}episode'],
        air_date=episode[f'{prefix}air_date'],
        air_datetime=episode[f'{prefix}air_datetime'],
        plot=episode[f'{prefix}plot'],
        runtime=episode[f'{prefix}runtime'],
        rating=float(rating) if rating is not None else None,
    )


def episode_watched_row_mapper(watched: RowMapping, prefix: str = '') -> EpisodeWatched:
    return EpisodeWatched(
        episode_number=watched[f'{prefix}episode_number'],
        times=watched[f'{prefix}times'] or 0,
        position=watched[f'{prefix}position'] or 0,
        watched_at=watched[f'{prefix}watched_at'],
    )
