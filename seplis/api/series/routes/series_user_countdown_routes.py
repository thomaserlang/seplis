from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_timeline_actions import (
    get_series_countdown,
)
from ..schemas.series_schemas import SeriesAndEpisode

router = APIRouter()


@router.get(
    '/countdown',
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def series_countdown_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
    page_query: Annotated[PageCursorQuery, Depends()],
) -> PageCursor[SeriesAndEpisode]:
    return await get_series_countdown(user_id=user.id, page_query=page_query)
