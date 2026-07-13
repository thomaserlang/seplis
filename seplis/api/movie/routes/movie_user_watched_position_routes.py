from typing import Annotated

from fastapi import APIRouter, Body, Response, Security

from seplis.api.dependencies import authenticated
from seplis.api.user import UserAuthenticated

from ..actions.movie_user_actions import (
    delete_movie_watched_position,
    get_movie_watched_position,
    set_movie_watched_position,
)
from ..schemas.movie_schemas import MovieWatched

router = APIRouter()


@router.get('/{movie_id}/watched-position', response_model=None)
async def get_position_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> MovieWatched | Response:
    watched = await get_movie_watched_position(movie_id=movie_id, user_id=user.id)
    return watched if watched else Response(status_code=204)


@router.put('/{movie_id}/watched-position', status_code=204)
async def set_position_route(
    movie_id: int,
    position: Annotated[int, Body(..., embed=True, ge=0, le=86400)],
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> None:
    await set_movie_watched_position(
        movie_id=movie_id, user_id=user.id, position=position
    )


@router.delete('/{movie_id}/watched-position', status_code=204)
async def delete_position_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> None:
    await delete_movie_watched_position(movie_id=movie_id, user_id=user.id)
