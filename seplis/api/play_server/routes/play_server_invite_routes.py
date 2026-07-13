from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.play_server_invite_actions import (
    accept_play_server_invite,
    create_play_server_invite,
    delete_play_server_invite,
    get_play_server_invites,
)
from ..schemas.play_server_schemas import (
    PlayServerInvite,
    PlayServerInviteCreate,
    PlayServerInviteId,
)

router = APIRouter()


@router.post(
    '/{play_server_id}/invites',
    status_code=201,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def create_play_server_invite_route(
    play_server_id: str,
    data: PlayServerInviteCreate,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> PlayServerInviteId:
    return await create_play_server_invite(
        play_server_id=play_server_id, owner_user_id=user.id, data=data
    )


@router.get(
    '/{play_server_id}/invites',
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def get_play_server_invites_route(
    play_server_id: str,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
    page_query: Annotated[PageCursorQuery, Depends()],
) -> PageCursor[PlayServerInvite]:
    return await get_play_server_invites(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        page_query=page_query,
    )


@router.delete(
    '/{play_server_id}/invites/{user_id}',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def delete_play_server_invite_route(
    play_server_id: str,
    user_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> None:
    await delete_play_server_invite(
        play_server_id=play_server_id, owner_user_id=user.id, user_id=user_id
    )


@router.post(
    '/accept-invite',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def accept_play_server_invite_route(
    data: PlayServerInviteId,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> None:
    await accept_play_server_invite(user_id=user.id, invite_id=data.invite_id)
