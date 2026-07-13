from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.play_server_actions import get_play_servers
from ..schemas.play_server_schemas import PlayServer

router = APIRouter()


@router.get(
    '',
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def get_play_servers_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:list_play_servers'])
    ],
    page_query: Annotated[PageCursorQuery, Depends()],
) -> PageCursor[PlayServer]:
    return await get_play_servers(user_id=user.id, page_query=page_query)
