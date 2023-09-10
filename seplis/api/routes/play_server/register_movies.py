from fastapi import Security
from ...dependencies import play_server_secret
from ... import models, schemas
from .router import router


@router.put('/{play_server_id}/movies', status_code=204)
async def register_play_server_movies_put(
    play_server_id: str,
    data: list[schemas.Play_server_movie_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_movie.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=False,
    )


@router.patch('/{play_server_id}/movies', status_code=204)
async def register_play_server_movie_patch(
    play_server_id: str,
    data: list[schemas.Play_server_movie_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_movie.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=True,
    )


@router.delete('/{play_server_id}/movies/{movie_id}', status_code=204)
async def delete_movie_from_play_server(
    play_server_id: str,
    movie_id: int,
    secret: str = Security(play_server_secret),
):
    await models.Play_server_movie.delete(
        play_server_id=play_server_id,
        movie_id=movie_id,
        play_server_secret=secret,
    )