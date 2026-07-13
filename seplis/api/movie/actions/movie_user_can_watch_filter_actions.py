from typing import Any

from seplis.api import exceptions

from ..models.movie_model import MMovie
from ..types.movie_filter_types import MovieQueryFilter


def filter_can_watch(query: Any, filter_query: MovieQueryFilter) -> Any:
    has_sort = (
        'user_play_server_movie_added_asc' in filter_query.sort
        or 'user_play_server_movie_added_desc' in filter_query.sort
    )
    if not filter_query.user_can_watch and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.NotSignedInException()
    from seplis.api.play_server.models.play_server_model import (
        MPlayServerAccess,
        MPlayServerMovie,
    )

    return query.where(
        MPlayServerAccess.user_id == filter_query.user.id,
        MPlayServerMovie.play_server_id == MPlayServerAccess.play_server_id,
        MPlayServerMovie.movie_id == MMovie.id,
    )
