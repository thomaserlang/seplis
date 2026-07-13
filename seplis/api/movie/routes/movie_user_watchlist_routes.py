from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated
from seplis.api.user import UserAuthenticated

from ..actions.movie_user_actions import (
    add_movie_watchlist,
    get_movie_watchlist,
    remove_movie_watchlist,
)
from ..schemas.movie_schemas import MovieWatchlist

router = APIRouter()


@router.get('/{movie_id}/watchlist')
async def get_watchlist_route(
    movie_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
) -> MovieWatchlist:
    return await get_movie_watchlist(movie_id=movie_id, user_id=user.id)


@router.put('/{movie_id}/watchlist', status_code=204)
async def add_to_watchlist_route(
    movie_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await add_movie_watchlist(movie_id=movie_id, user_id=user.id)


@router.delete('/{movie_id}/watchlist', status_code=204)
async def remove_from_watchlist_route(
    movie_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await remove_movie_watchlist(movie_id=movie_id, user_id=user.id)
