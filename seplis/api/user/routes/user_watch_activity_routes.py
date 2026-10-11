from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated

from ..actions.user_watch_activity_actions import get_user_watch_activity
from ..schemas.user_authentication_schemas import UserAuthenticated
from ..schemas.user_watch_activity_schemas import UserWatchActivityMonth

router = APIRouter(prefix='/users')


@router.get('/me/watch-activity', description='**Scope required:** `user:view_stats`')
async def get_watch_activity_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_stats'])
    ],
) -> list[UserWatchActivityMonth]:
    return await get_user_watch_activity(user.id)
