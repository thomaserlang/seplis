from urllib.parse import urljoin
from fastapi import APIRouter, Depends, Response, Security
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import logger

router = APIRouter(prefix='/2/series/{series_id}/episode-to-watch')

DESCRIPTION = """
Returns which episode to watch for a series.

* Return episode 1 if the user has not watched any episodes.
* If the user is watching an episode and it is not completed 
    return that one.
* If the latest episode watched by the user is completed
    return the latest + 1.

If the next episode does not exist or the series has no
episodes the result will be empty 204`.

:returns: episode dict with "user_watched" field.
    {
        "number": 1,
        "title": "asd",
        "user_watched": {
            "times": 1,
            "position": 100,
        }
    }

"""

@router.get('', response_model=schemas.Episode_with_user_watched, description=DESCRIPTION)
async def get_episode_to_watch(
    series_id: int | str,
    response: Response,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
    session: AsyncSession=Depends(get_session),
):
    ew = await session.execute(sa.select(
        models.Episode_watched.episode_number,
        models.Episode_watched.position,
    ).where(
        models.Episode_watching.user_id == user.id,
        models.Episode_watching.show_id == series_id,
        models.Episode_watched.show_id == models.Episode_watching.show_id,
        models.Episode_watched.user_id == models.Episode_watching.user_id,
        models.Episode_watched.episode_number ==\
            models.Episode_watching.episode_number,
    ))
    ew = ew.first()

    episode_number = 1
    if ew:
        episode_number = ew.episode_number
        if ew.position == 0:
            episode_number += 1

    e = await session.execute(sa.select(
        models.Episode,
        models.Episode_watched,
    ).where(
        models.Episode.show_id == series_id,
        models.Episode.number == episode_number,
    ).join(
        models.Episode_watched, sa.and_(
            models.Episode_watched.user_id == user.id,
            models.Episode_watched.show_id == models.Episode.show_id,
            models.Episode_watched.episode_number == models.Episode.number,
        ),
        isouter=True
    ))
    e = e.first()
    
    if not e:
        response.status_code = 204
        return

    episode = schemas.Episode_with_user_watched.from_orm(e.Episode)
    if e.Episode_watched:
        episode.user_watched = schemas.Episode_watched.from_orm(e.Episode_watched)
    return episode