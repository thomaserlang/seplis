from typing import Annotated

from fastapi import APIRouter, Body, Response, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.episode_actions import (
    delete_watched_position,
    get_watched_position,
    set_watched_position,
)
from ..schemas.episode_schemas import EpisodeWatched

router = APIRouter()


@router.get(
    '/{series_id}/episodes/{episode_number}/watched-position',
    response_model=None,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def get_position_route(
    series_id: int,
    episode_number: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> EpisodeWatched | Response:
    watched = await get_watched_position(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user.id,
    )
    if not watched:
        return Response(status_code=204)
    return watched


@router.put(
    '/{series_id}/episodes/{episode_number}/watched-position',
    status_code=204,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def set_position_route(
    series_id: int,
    episode_number: int,
    position: Annotated[int, Body(..., embed=True, ge=0, le=86400)],
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> None:
    await set_watched_position(
        series_id=series_id,
        episode_number=episode_number,
        position=position,
        user_id=user.id,
    )


@router.delete(
    '/{series_id}/episodes/{episode_number}/watched-position',
    status_code=204,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def delete_position_route(
    series_id: int,
    episode_number: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> None:
    await delete_watched_position(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user.id,
    )
