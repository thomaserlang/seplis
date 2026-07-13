from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.play_server_access_actions import (
    get_users_with_access,
    leave_play_server,
    remove_user_access,
)
from ..actions.play_server_actions import (
    get_play_servers_with_access,
)
from ..schemas.play_server_schemas import PlayServerAccess, PlayServerWithUrl

router = APIRouter()


@router.get(
    '/access',
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def get_play_servers_with_access_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:list_play_servers'])
    ],
    page_query: Annotated[PageCursorQuery, Depends()],
) -> PageCursor[PlayServerWithUrl]:
    return await get_play_servers_with_access(user_id=user.id, page_query=page_query)


@router.get(
    '/{play_server_id}/access',
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def get_users_with_access_route(
    play_server_id: str,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
    page_query: Annotated[PageCursorQuery, Depends()],
) -> PageCursor[PlayServerAccess]:
    return await get_users_with_access(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        page_query=page_query,
    )


@router.delete(
    '/{play_server_id}/access/{user_id}',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def remove_user_access_route(
    play_server_id: str,
    user_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> None:
    await remove_user_access(
        play_server_id=play_server_id, owner_user_id=user.id, user_id=user_id
    )


@router.delete(
    '/{play_server_id}/access/me',
    status_code=204,
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def leave_play_server_route(
    play_server_id: str,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:list_play_servers'])
    ],
) -> None:
    await leave_play_server(play_server_id=play_server_id, user_id=user.id)
