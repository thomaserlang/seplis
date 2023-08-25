import sqlalchemy as sa
from fastapi import APIRouter, Depends, Response, Security
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ..expand.episodes import expand_user_can_watch

router = APIRouter(prefix='/2/series/{series_id}/episode-last-watched')

DESCRIPTION = """
Get the user's latest watched episode for a series.
The episode must be the latest completed.
"""

@router.get('', response_model=schemas.Episode, description=DESCRIPTION)
async def get_last_watched_episode(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
    session: AsyncSession=Depends(get_session),
):
    eps = await session.execute(sa.select(
        models.Episode,
        models.Episode_watched,
    ).where(
        models.Episode_watched.user_id == user.id,
        models.Episode_watched.series_id == series_id,
        models.Episode.series_id == models.Episode_watched.series_id,
        models.Episode.number == models.Episode_watched.episode_number,
    ).order_by(
        sa.desc(models.Episode_watched.watched_at),
        sa.desc(models.Episode_watched.episode_number),
    ).limit(2))
    eps = eps.all()
    
    if not eps:
        return Response(status_code=204)
    
    e = eps[0]
    if len(eps) == 1:
        if eps[0].Episode_watched.position > 0:
            return Response(status_code=204)
    else:
        if eps[0].Episode_watched.position > 0:
            e = eps[1]

    episode = schemas.Episode.model_validate(e.Episode)
    episode.user_watched = schemas.Episode_watched.model_validate(e.Episode_watched)
    await expand_user_can_watch(series_id=series_id, user_id=user.id, episodes=[episode], session=session)
    return episode