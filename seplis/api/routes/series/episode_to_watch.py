import sqlalchemy as sa
from fastapi import Depends, Response, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
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


@router.get(
    '/{series_id}/episode-to-watch',
    response_model=schemas.Episode,
    description=DESCRIPTION,
)
async def get_episode_to_watch(
    series_id: int | str,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
    session: AsyncSession = Depends(get_session),
):
    ew = await session.execute(
        sa.select(
            models.MEpisodeWatched.episode_number,
            models.MEpisodeWatched.position,
        ).where(
            models.MEpisodeLastWatched.user_id == user.id,
            models.MEpisodeLastWatched.series_id == series_id,
            models.MEpisodeWatched.series_id == models.MEpisodeLastWatched.series_id,
            models.MEpisodeWatched.user_id == models.MEpisodeLastWatched.user_id,
            models.MEpisodeWatched.episode_number
            == models.MEpisodeLastWatched.episode_number,
        )
    )
    ew = ew.first()

    episode_number = 1
    if ew:
        episode_number = ew.episode_number
        if ew.position == 0:
            episode_number += 1

    e = await session.execute(
        sa.select(
            models.MEpisode,
            models.MEpisodeWatched,
        )
        .where(
            models.MEpisode.series_id == series_id,
            models.MEpisode.number == episode_number,
        )
        .join(
            models.MEpisodeWatched,
            sa.and_(
                models.MEpisodeWatched.user_id == user.id,
                models.MEpisodeWatched.series_id == models.MEpisode.series_id,
                models.MEpisodeWatched.episode_number == models.MEpisode.number,
            ),
            isouter=True,
        )
    )
    e = e.first()

    if not e:
        return Response(status_code=204)

    episode = schemas.Episode.model_validate(e.MEpisode)
    episode.user_watched = (
        schemas.Episode_watched.model_validate(e.MEpisodeWatched)
        if e.MEpisodeWatched
        else schemas.Episode_watched(episode_number=e.MEpisode.number)
    )
    await expand_user_can_watch(
        series_id=series_id, user_id=user.id, episodes=[episode], session=session
    )
    return episode
