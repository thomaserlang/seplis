from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import play_server_secret
from ..actions.play_server_register_actions import (
    delete_episode_from_play_server,
    register_play_server_episodes,
)
from ..schemas.play_server_schemas import PlayServerEpisodeCreate

router = APIRouter()


@router.put('/{play_server_id}/episodes', status_code=204)
async def register_play_server_episode_put_route(
    play_server_id: str,
    data: list[PlayServerEpisodeCreate],
    secret: Annotated[str, Security(play_server_secret)],
) -> None:
    await register_play_server_episodes(
        play_server_id=play_server_id, secret=secret, data=data, patch=False
    )


@router.patch('/{play_server_id}/episodes', status_code=204)
async def register_play_server_episode_patch_route(
    play_server_id: str,
    data: list[PlayServerEpisodeCreate],
    secret: Annotated[str, Security(play_server_secret)],
) -> None:
    await register_play_server_episodes(
        play_server_id=play_server_id, secret=secret, data=data, patch=True
    )


@router.delete(
    '/{play_server_id}/series/{series_id}/episodes/{episode_number}', status_code=204
)
async def delete_episode_from_play_server_route(
    play_server_id: str,
    series_id: int,
    episode_number: int,
    secret: Annotated[str, Security(play_server_secret)],
) -> None:
    await delete_episode_from_play_server(
        play_server_id=play_server_id,
        series_id=series_id,
        episode_number=episode_number,
        secret=secret,
    )
