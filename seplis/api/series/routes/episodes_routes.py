from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import (
    get_current_user_no_raise,
    get_expand,
)
from ...user import UserAuthenticated
from ..actions.episode_actions import get_episodes
from ..schemas.episode_schemas import Episode

router = APIRouter()


@router.get('/{series_id}/episodes')
async def get_episodes_route(
    series_id: int,
    expand: Annotated[list[str] | None, Depends(get_expand)],
    user: Annotated[UserAuthenticated | None, Depends(get_current_user_no_raise)],
    page_cursor: Annotated[PageCursorQuery, Depends()],
    season: int | None = None,
    episode: int | None = None,
    number: int | None = None,
    air_date: date | None = None,
    air_date_ge: date | None = None,
    air_date_le: date | None = None,
) -> PageCursor[Episode]:
    return await get_episodes(
        series_id=series_id,
        season=season,
        episode=episode,
        number=number,
        air_date=air_date,
        air_date_ge=air_date_ge,
        air_date_le=air_date_le,
        expand=expand,
        user=user,
        page_query=page_cursor,
    )
