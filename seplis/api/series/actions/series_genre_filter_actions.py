from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import aliased

from ..models.series_model import MSeries, MSeriesGenre
from ..types.series_filter_types import SeriesQueryFilter


def filter_genres(query: Any, filter_query: SeriesQueryFilter) -> Any:
    if filter_query.genre_id:
        genre_alias = aliased(MSeriesGenre)
        query = query.where(
            sa.exists(
                sa.select(1).where(
                    genre_alias.series_id == MSeries.id,
                    genre_alias.genre_id.in_(filter_query.genre_id),
                )
            )
        )

    if filter_query.not_genre_id:
        genre_alias = aliased(MSeriesGenre)
        query = query.where(
            ~sa.exists(
                sa.select(1).where(
                    genre_alias.series_id == MSeries.id,
                    genre_alias.genre_id.in_(filter_query.not_genre_id),
                )
            )
        )

    return query
