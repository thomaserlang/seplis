from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated
from seplis.api.user import UserAuthenticated

from ..actions.movie_stats_actions import get_user_movie_stats
from ..schemas.movie_stats_schemas import UserMovieStats

router = APIRouter()


@router.get('/user-stats', description='**Scope required:** `user:view_stats`')
async def get_user_stats_route(
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_stats'])
    ],
) -> UserMovieStats:
    return await get_user_movie_stats(user.id)
