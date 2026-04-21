import sqlalchemy as sa
from fastapi import Depends, Response, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from ...expand.episodes import expand_user_can_watch
from .router import router

DESCRIPTION = """
Get the user's latest watched episode for a series.
The episode must be the latest completed.

**Required scope:** `user:progress`
"""


@router.get(
    '/{series_id}/episode-last-watched',
    response_model=schemas.Episode,
    description=DESCRIPTION,
)
async def get_last_watched_episode(
    series_id: int,
    user: User_authenticated = Security(authenticated, scopes=['user:progress']),
    session: AsyncSession = Depends(get_session),
):
    eps = await session.execute(
        sa.select(
            models.MEpisode,
            models.MEpisodeWatched,
        )
        .where(
            models.MEpisodeWatched.user_id == user.id,
            models.MEpisodeWatched.series_id == series_id,
            models.MEpisode.series_id == models.MEpisodeWatched.series_id,
            models.MEpisode.number == models.MEpisodeWatched.episode_number,
        )
        .order_by(
            sa.desc(models.MEpisodeWatched.watched_at),
            sa.desc(models.MEpisodeWatched.episode_number),
        )
        .limit(2)
    )
    eps = eps.all()

    if not eps:
        return Response(status_code=204)

    e = eps[0]
    if len(eps) == 1:
        if eps[0].MEpisodeWatched.position > 0:
            return Response(status_code=204)
    else:
        if eps[0].MEpisodeWatched.position > 0:
            e = eps[1]

    episode = schemas.Episode.model_validate(e.MEpisode)
    episode.user_watched = schemas.Episode_watched.model_validate(e.MEpisodeWatched)
    await expand_user_can_watch(
        series_id=series_id, user_id=user.id, episodes=[episode], session=session
    )
    return episode
