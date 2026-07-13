from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.play_server_actions import (
    create_play_server,
    delete_play_server,
    get_play_server,
    update_play_server,
)
from ..schemas.play_server_schemas import (
    PlayServerCreate,
    PlayServerUpdate,
    PlayServerWithUrl,
)

router = APIRouter()


@router.post(
    '',
    status_code=201,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def create_play_server_route(
    data: PlayServerCreate,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> PlayServerWithUrl:
    return await create_play_server(data=data, user_id=user.id)


@router.put(
    '/{play_server_id}',
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def update_play_server_route(
    play_server_id: str,
    data: PlayServerUpdate,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> PlayServerWithUrl:
    return await update_play_server(
        data=data, play_server_id=play_server_id, user_id=user.id
    )


@router.get(
    '/{play_server_id}',
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def get_play_server_route(
    play_server_id: str,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:list_play_servers'])
    ],
) -> PlayServerWithUrl:
    return await get_play_server(play_server_id=play_server_id, user_id=user.id)


@router.delete(
    '/{play_server_id}',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def delete_play_server_route(
    play_server_id: str,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_servers'])
    ],
) -> None:
    await delete_play_server(play_server_id=play_server_id, user_id=user.id)
