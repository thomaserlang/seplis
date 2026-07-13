from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.play_server import PlayRequest

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_play_server_actions import (
    get_episode_play_servers,
)

router = APIRouter()


@router.get(
    '/{series_id}/episodes/{episode_number}/play-servers',
    description="""
            **Scope required:** `user:play`
            """,
)
async def get_episode_play_servers_route(
    series_id: int,
    episode_number: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:play'])],
) -> list[PlayRequest]:
    return await get_episode_play_servers(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user.id,
    )
