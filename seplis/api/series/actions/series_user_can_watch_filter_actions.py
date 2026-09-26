from typing import Any

from seplis.api import exceptions
from seplis.api.play_server.models.play_server_model import (
    MPlayServerAccess,
    MPlayServerEpisode,
)

from ..models.series_model import MSeries
from ..types.series_filter_types import SeriesQueryFilter


def filter_user_can_watch(
    query: Any, filter_query: SeriesQueryFilter, episode_number: Any = None
) -> Any:
    has_sort = (
        'user_play_server_series_added_asc' in filter_query.sort
        or 'user_play_server_series_added_desc' in filter_query.sort
    )
    if not filter_query.user_can_watch and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()
    return filter_user_can_watch_query(
        query, filter_query.user.id, episode_number=episode_number or 1
    )


def filter_user_can_watch_query(query: Any, user_id: int, episode_number: Any) -> Any:
    return query.where(
        MPlayServerAccess.user_id == user_id,
        MPlayServerEpisode.play_server_id == MPlayServerAccess.play_server_id,
        MPlayServerEpisode.series_id == MSeries.id,
        MPlayServerEpisode.episode_number == episode_number,
    )
