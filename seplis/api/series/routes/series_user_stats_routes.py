from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_user_actions import get_user_stats
from ..schemas.series_schemas import SeriesUserStats

router = APIRouter()


@router.get(
    '/{series_id}/user-stats',
    description="""
            **Scope required:** `user:view_stats`
            """,
)
async def get_user_stats_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_stats'])
    ],
) -> SeriesUserStats:
    return await get_user_stats(series_id=series_id, user_id=user.id)
