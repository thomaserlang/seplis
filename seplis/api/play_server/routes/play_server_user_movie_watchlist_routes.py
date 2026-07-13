from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from seplis.api.movie.types.movie_filter_types import MovieQueryFilterDep
from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ..actions.play_server_user_watchlist_actions import (
    get_play_server_users_movie_watchlist,
)
from ..schemas.play_server_schemas import RadarrResponse

router = APIRouter()


@router.get('/{play_server_id}/users-movie-watchlist', response_model=None)
async def get_play_server_users_movie_watchlist_route(
    play_server_id: str,
    page_query: Annotated[PageCursorQuery, Depends()],
    filter_query: MovieQueryFilterDep,
    added_at_ge: datetime | None = None,
    added_at_le: datetime | None = None,
    response_format: Literal['standard', 'radarr'] = 'standard',
) -> PageCursor | list[RadarrResponse]:
    return await get_play_server_users_movie_watchlist(
        play_server_id=play_server_id,
        page_query=page_query,
        filter_query=filter_query,
        added_at_ge=added_at_ge,
        added_at_le=added_at_le,
        response_format=response_format,
    )
