from typing import Annotated

from fastapi import APIRouter, Query, Security

from seplis.api.page_cursor import PageCursor
from seplis.api.user import UserAuthenticated

from ...dependencies import authenticated
from ..actions.user_watched_actions import get_user_watched
from ..schemas.user_watched_schemas import UserWatched

router = APIRouter(prefix='/users')


@router.get(
    '/me/watched',
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def get_user_watched_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
    user_can_watch: Annotated[bool | None, Query()] = None,
) -> PageCursor[UserWatched]:
    return await get_user_watched(user_id=user.id, user_can_watch=user_can_watch)
