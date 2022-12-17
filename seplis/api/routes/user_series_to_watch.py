from fastapi import APIRouter, Depends, Request, Security
import sqlalchemy as sa
from datetime import datetime, timezone, timedelta
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/series-to-watch')

@router.get('', response_model=schemas.Page_result[schemas.Series_and_episode])
async def get_series_recently_aired(
    request: Request,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    episodes_query = sa.select(
        models.Episode_watched.series_id,
        sa.func.max(models.Episode_watched.episode_number).label('episode_number'),
    ).where(
        models.Episode_watched.user_id == user.id,
        models.Series_follower.user_id == models.Episode_watched.user_id,
        models.Series_follower.series_id == models.Episode_watched.series_id,
        models.Episode_watched.times > 0,
    ).group_by(models.Episode_watched.series_id).subquery()
    query = sa.select(models.Series, models.Episode).where(
        models.Series.id == episodes_query.c.show_id,
        models.Episode.series_id == models.Series.id,
        models.Episode.number == episodes_query.c.episode_number+1,
        models.Episode.air_datetime <= datetime.now(tz=timezone.utc),
    ).order_by(
        sa.desc(models.Episode.air_datetime), 
        models.Episode.series_id,
    )

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request, scalars=False)
    p.items = [schemas.Series_and_episode(series=item.Series, episode=item.Episode) for item in p.items]
    return p