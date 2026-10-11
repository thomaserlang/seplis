from typing import Annotated

from fastapi import APIRouter, Query, Security

from seplis.api.dependencies import authenticated

from ..actions.user_watch_activity_actions import get_user_watch_activity
from ..schemas.user_authentication_schemas import UserAuthenticated
from ..schemas.user_watch_activity_schemas import UserWatchActivityPeriod

router = APIRouter(prefix='/users')


@router.get('/me/watch-activity', description='**Scope required:** `user:view_stats`')
async def get_watch_activity_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_stats'])
    ],
    year: Annotated[int, Query(ge=1, le=9998)],
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
) -> list[UserWatchActivityPeriod]:
    return await get_user_watch_activity(user.id, year=year, month=month)
