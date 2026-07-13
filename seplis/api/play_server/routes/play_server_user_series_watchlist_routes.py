from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.series.types.series_filter_types import SeriesQueryFilterDep

from ..actions.play_server_user_watchlist_actions import (
    get_play_server_users_series_watchlist,
)
from ..schemas.play_server_schemas import SonarrResponse

router = APIRouter()


@router.get('/{play_server_id}/users-series-watchlist', response_model=None)
async def get_play_servers_user_series_watchlist_route(
    play_server_id: str,
    page_query: Annotated[PageCursorQuery, Depends()],
    filter_query: SeriesQueryFilterDep,
    added_at_ge: datetime | None = None,
    added_at_le: datetime | None = None,
    response_format: Literal['standard', 'sonarr'] = 'standard',
) -> PageCursor | list[SonarrResponse]:
    return await get_play_server_users_series_watchlist(
        play_server_id=play_server_id,
        page_query=page_query,
        filter_query=filter_query,
        added_at_ge=added_at_ge,
        added_at_le=added_at_le,
        response_format=response_format,
    )
