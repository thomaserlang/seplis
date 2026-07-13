from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.user import UserSeriesStats

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_user_actions import get_all_user_stats

router = APIRouter()


@router.get(
    '/user-stats',
    description="""
            **Scope required:** `user:view_stats`
            """,
)
async def get_series_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_stats'])
    ],
) -> UserSeriesStats:
    return await get_all_user_stats(user.id)
