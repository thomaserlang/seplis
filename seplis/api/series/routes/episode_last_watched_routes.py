from typing import Annotated

from fastapi import APIRouter, Response, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.episode_actions import (
    get_last_watched_episode,
)
from ..schemas.episode_schemas import Episode

router = APIRouter()
DESCRIPTION = """
Get the user's latest watched episode for a series.
The episode must be the latest completed.

**Required scope:** `user:progress`
"""


@router.get(
    '/{series_id}/episode-last-watched', response_model=None, description=DESCRIPTION
)
async def get_last_watched_episode_route(
    series_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> Episode | Response:
    episode = await get_last_watched_episode(series_id=series_id, user_id=user.id)
    if not episode:
        return Response(status_code=204)
    return episode
