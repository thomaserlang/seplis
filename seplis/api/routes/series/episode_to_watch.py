import sqlalchemy as sa
from fastapi import Depends, Response, Security
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from ...expand.episodes import expand_user_can_watch
from .router import router

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

@router.get('/{series_id}/episode-to-watch', response_model=schemas.Episode, description=DESCRIPTION)
async def get_episode_to_watch(
    series_id: int | str,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
    session: AsyncSession=Depends(get_session),
):
    ew = await session.execute(sa.select(
        models.Episode_watched.episode_number,
        models.Episode_watched.position,
    ).where(
        models.Episode_last_watched.user_id == user.id,
        models.Episode_last_watched.series_id == series_id,
        models.Episode_watched.series_id == models.Episode_last_watched.series_id,
        models.Episode_watched.user_id == models.Episode_last_watched.user_id,
        models.Episode_watched.episode_number ==\
            models.Episode_last_watched.episode_number,
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
        models.Episode.series_id == series_id,
        models.Episode.number == episode_number,
    ).join(
        models.Episode_watched, sa.and_(
            models.Episode_watched.user_id == user.id,
            models.Episode_watched.series_id == models.Episode.series_id,
            models.Episode_watched.episode_number == models.Episode.number,
        ),
        isouter=True
    ))
    e = e.first()
    
    if not e:
        return Response(status_code=204)

    episode = schemas.Episode.model_validate(e.Episode)
    episode.user_watched = schemas.Episode_watched.model_validate(e.Episode_watched) if e.Episode_watched else \
        schemas.Episode_watched(episode_number=e.Episode.number)    
    await expand_user_can_watch(series_id=series_id, user_id=user.id, episodes=[episode], session=session)
    return episode