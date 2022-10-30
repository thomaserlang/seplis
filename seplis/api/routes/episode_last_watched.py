from fastapi import APIRouter, Depends, Response, Security
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import logger

router = APIRouter(prefix='/2/series/{series_id}/episode-last-watched')

DESCRIPTION = """
Get the user's latest watched episode for a series.
The episode must be the latest completed.
"""

@router.get('', response_model=schemas.Episode_with_user_watched, description=DESCRIPTION)
async def get_last_watched_episode(
    series_id: int,
    response: Response,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
    session: AsyncSession=Depends(get_session),
):
    eps = await session.execute(sa.select(
        models.Episode,
        models.Episode_watched,
    ).where(
        models.Episode_watched.user_id == user.id,
        models.Episode_watched.show_id == series_id,
        models.Episode.show_id == models.Episode_watched.show_id,
        models.Episode.number == models.Episode_watched.episode_number,
    ).order_by(
        sa.desc(models.Episode_watched.watched_at),
        sa.desc(models.Episode_watched.episode_number),
    ).limit(2))
    eps = eps.all()
    
    if not eps:
        response.status_code = 204
        return
        
    e = eps[0]
    if len(eps) == 1:
        if eps[0].Episode_watched.position > 0:
            response.status_code = 204
            return
    else:
        if eps[0].Episode_watched.position > 0:
            e = eps[1]

    episode = schemas.Episode_with_user_watched.from_orm(e.Episode)
    episode.user_watched = schemas.Episode_watched.from_orm(e.Episode_watched)
    return episode