from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import play_server_secret
from ..actions.play_server_register_actions import (
    delete_movie_from_play_server,
    register_play_server_movies,
)
from ..schemas.play_server_schemas import PlayServerMovieCreate

router = APIRouter()


@router.put('/{play_server_id}/movies', status_code=204)
async def register_play_server_movies_put_route(
    play_server_id: str,
    data: list[PlayServerMovieCreate],
    secret: Annotated[str, Security(play_server_secret)],
) -> None:
    await register_play_server_movies(
        play_server_id=play_server_id, secret=secret, data=data, patch=False
    )


@router.patch('/{play_server_id}/movies', status_code=204)
async def register_play_server_movie_patch_route(
    play_server_id: str,
    data: list[PlayServerMovieCreate],
    secret: Annotated[str, Security(play_server_secret)],
) -> None:
    await register_play_server_movies(
        play_server_id=play_server_id, secret=secret, data=data, patch=True
    )


@router.delete('/{play_server_id}/movies/{movie_id}', status_code=204)
async def delete_movie_from_play_server_route(
    play_server_id: str,
    movie_id: int,
    secret: Annotated[str, Security(play_server_secret)],
) -> None:
    await delete_movie_from_play_server(
        play_server_id=play_server_id, movie_id=movie_id, secret=secret
    )
