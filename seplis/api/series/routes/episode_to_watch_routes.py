from typing import Annotated

from fastapi import APIRouter, Response, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.episode_actions import get_episode_to_watch
from ..schemas.episode_schemas import Episode

router = APIRouter()
DESCRIPTION = """
Returns which episode to watch for a series.

* Return episode 1 if the user has not watched any episodes.
* If the user is watching an episode and it is not completed
    return that one.
* If the latest episode watched by the user is completed
    return the latest + 1.

If the next episode does not exist or the series has no
episodes the result will be empty 204`.

**Required scope:** `user:progress`
"""


@router.get('/{series_id}/episode-to-watch', response_model=None, description=DESCRIPTION)
async def get_episode_to_watch_route(
    series_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> Episode | Response:
    episode = await get_episode_to_watch(series_id=series_id, user_id=user.id)
    if not episode:
        return Response(status_code=204)
    return episode
