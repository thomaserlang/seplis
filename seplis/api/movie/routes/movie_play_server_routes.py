from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated
from seplis.api.play_server import PlayRequest
from seplis.api.user import UserAuthenticated

from ..actions.movie_play_server_actions import get_movie_play_servers

router = APIRouter()


@router.get('/{movie_id}/play-servers')
async def get_movie_play_servers_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:play'])],
) -> list[PlayRequest]:
    return await get_movie_play_servers(movie_id=movie_id, user_id=user.id)
