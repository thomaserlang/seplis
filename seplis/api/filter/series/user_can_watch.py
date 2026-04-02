from typing import Any

from ... import exceptions, models
from .query_filter_schema import Series_query_filter


def filter_user_can_watch(
    query: Any, filter_query: Series_query_filter, episode_number: Any = None
):
    has_sort = (
        'user_play_server_series_added_asc' in filter_query.sort
        or 'user_play_server_series_added_desc' in filter_query.sort
    )
    if not filter_query.user_can_watch and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    return filter_user_can_watch_query(
        query, filter_query.user.id, episode_number=episode_number or 1
    )


def filter_user_can_watch_query(query: Any, user_id: int, episode_number: Any):
    return query.where(
        models.MPlayServerAccess.user_id == user_id,
        models.MPlayServerEpisode.play_server_id
        == models.MPlayServerAccess.play_server_id,
        models.MPlayServerEpisode.series_id == models.MSeries.id,
        models.MPlayServerEpisode.episode_number == episode_number,
    )
