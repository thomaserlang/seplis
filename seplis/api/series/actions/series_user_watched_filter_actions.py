from typing import Any

import sqlalchemy as sa

from seplis.api import exceptions

from ..models.episode_model import MEpisodeLastWatched, MEpisodeWatched
from ..models.series_model import MSeries
from ..types.series_filter_types import SeriesQueryFilter


def filter_has_watched(query: Any, filter_query: SeriesQueryFilter) -> Any:
    has_sort = (
        'user_last_episode_watched_at_asc' in filter_query.sort
        or 'user_last_episode_watched_at_desc' in filter_query.sort
    )

    if filter_query.user_has_watched is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()
    if filter_query.user_has_watched or has_sort:
        return query.where(
            MEpisodeLastWatched.user_id == filter_query.user.id,
            MSeries.id == MEpisodeLastWatched.series_id,
            MEpisodeWatched.user_id == MEpisodeLastWatched.user_id,
            MEpisodeWatched.series_id == MEpisodeLastWatched.series_id,
            MEpisodeWatched.episode_number == MEpisodeLastWatched.episode_number,
        )
    if not filter_query.user_has_watched:
        e = sa.select(1).where(
            MEpisodeLastWatched.user_id == filter_query.user.id,
            MEpisodeLastWatched.series_id == MSeries.id,
        )
        return query.where(sa.not_(sa.exists(e)))
    return query
