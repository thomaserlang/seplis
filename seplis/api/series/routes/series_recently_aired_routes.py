from typing import Annotated

from fastapi import APIRouter, Depends, Query

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ..actions.series_timeline_actions import (
    get_series_recently_aired,
)
from ..schemas.series_schemas import SeriesAndEpisode
from ..types.series_filter_types import SeriesQueryFilterDep

router = APIRouter()
RecentDays = Annotated[int, Query(ge=0, le=10)]


@router.get('/recently-aired')
async def get_series_recently_aired_route(
    page_cursor: Annotated[PageCursorQuery, Depends()],
    filter_query: SeriesQueryFilterDep,
    days_ahead: RecentDays = 0,
    days_behind: RecentDays = 7,
) -> PageCursor[SeriesAndEpisode]:
    return await get_series_recently_aired(
        page_query=page_cursor,
        filter_query=filter_query,
        days_ahead=days_ahead,
        days_behind=days_behind,
    )
