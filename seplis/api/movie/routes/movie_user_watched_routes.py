from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated
from seplis.api.user import UserAuthenticated

from ..actions.movie_user_actions import (
    decrement_movie_watched,
    get_movie_watched,
    increment_movie_watched,
)
from ..schemas.movie_schemas import MovieWatched, MovieWatchedIncrement

router = APIRouter()


@router.get('/{movie_id}/watched')
async def get_watched_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> MovieWatched:
    return await get_movie_watched(movie_id=movie_id, user_id=user.id)


@router.post('/{movie_id}/watched')
async def watched_increment_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
    request: MovieWatchedIncrement | None = None,
) -> MovieWatched:
    return await increment_movie_watched(
        movie_id=movie_id, user_id=user.id, data=request or {}
    )


@router.delete('/{movie_id}/watched')
async def watched_decrement_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> MovieWatched:
    return await decrement_movie_watched(movie_id=movie_id, user_id=user.id)
