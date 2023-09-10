from fastapi import Security
from ...dependencies import play_server_secret
from ... import models, schemas
from .router import router


@router.put('/{play_server_id}/episodes', status_code=204)
async def register_play_server_episode_put(
    play_server_id: str,
    data: list[schemas.Play_server_episode_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_episode.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=False,
    )


@router.patch('/{play_server_id}/episodes', status_code=204)
async def register_play_server_episode_patch(
    play_server_id: str,
    data: list[schemas.Play_server_episode_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_episode.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=True,
    )


@router.delete('/{play_server_id}/series/{series_id}/episodes/{episode_number}', status_code=204)
async def delete_episode_from_play_server(
    play_server_id: str,
    series_id: int,
    episode_number: int,
    secret: str = Security(play_server_secret),
):
    await models.Play_server_episode.delete(
        play_server_id=play_server_id,
        series_id=series_id,
        episode_number=episode_number,
        play_server_secret=secret,
    )