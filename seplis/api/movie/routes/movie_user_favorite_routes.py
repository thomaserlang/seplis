from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated
from seplis.api.user import UserAuthenticated

from ..actions.movie_user_actions import (
    add_movie_favorite,
    get_movie_favorite,
    remove_movie_favorite,
)
from ..schemas.movie_schemas import MovieFavorite

router = APIRouter()


@router.get('/{movie_id}/favorite')
async def get_favorite_route(
    movie_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
) -> MovieFavorite:
    return await get_movie_favorite(movie_id=movie_id, user_id=user.id)


@router.put('/{movie_id}/favorite', status_code=204)
async def add_to_favorite_route(
    movie_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await add_movie_favorite(movie_id=movie_id, user_id=user.id)


@router.delete('/{movie_id}/favorite', status_code=204)
async def remove_from_favorite_route(
    movie_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await remove_movie_favorite(movie_id=movie_id, user_id=user.id)
