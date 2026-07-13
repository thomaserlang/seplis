from typing import Annotated

from fastapi import APIRouter, Body, Path, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.episode_actions import (
    decrement_watched,
    get_watched,
    increment_watched,
    increment_watched_range,
)
from ..schemas.episode_schemas import EpisodeWatched, EpisodeWatchedIncrement

router = APIRouter()
PositiveInt = Annotated[int, Path(ge=1)]


@router.get(
    '/{series_id}/episodes/{episode_number}/watched',
    description="""
            **Scope required:** `user:progress`
            """,
)
async def get_watched_route(
    series_id: PositiveInt,
    episode_number: PositiveInt,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> EpisodeWatched:
    return await get_watched(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user.id,
    )


@router.post(
    '/{series_id}/episodes/{episode_number}/watched',
    description="""
            **Scope required:** `user:progress`
            """,
)
async def watched_increment_route(
    series_id: PositiveInt,
    episode_number: PositiveInt,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
    request: EpisodeWatchedIncrement | None = None,
) -> EpisodeWatched:
    return await increment_watched(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user.id,
        data=request,
    )


@router.delete(
    '/{series_id}/episodes/{episode_number}/watched',
    description="""
            **Scope required:** `user:progress`
            """,
)
async def watched_decrement_route(
    series_id: PositiveInt,
    episode_number: PositiveInt,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> EpisodeWatched:
    return await decrement_watched(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user.id,
    )


@router.post(
    '/{series_id}/episodes/watched-range',
    status_code=204,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def watched_increment_range_route(
    series_id: PositiveInt,
    from_episode_number: Annotated[int, Body(..., embed=True, ge=1)],
    to_episode_number: Annotated[int, Body(..., embed=True, ge=1)],
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
    request: EpisodeWatchedIncrement | None = None,
) -> None:
    await increment_watched_range(
        series_id=series_id,
        from_episode_number=from_episode_number,
        to_episode_number=to_episode_number,
        user_id=user.id,
        data=request,
    )
