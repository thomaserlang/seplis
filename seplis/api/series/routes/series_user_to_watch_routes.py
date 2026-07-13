from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_timeline_actions import get_user_series_to_watch
from ..schemas.series_schemas import SeriesAndEpisode
from ..types.series_filter_types import SeriesQueryFilterDep

router = APIRouter()


@router.get(
    '/to-watch',
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def get_user_series_to_watch_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
    page_cursor: Annotated[PageCursorQuery, Depends()],
    filter_query: SeriesQueryFilterDep,
) -> PageCursor[SeriesAndEpisode]:
    return await get_user_series_to_watch(
        user_id=user.id,
        page_query=page_cursor,
        filter_query=filter_query,
    )
