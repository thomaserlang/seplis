from fastapi import APIRouter, Depends, Query, Security
import sqlalchemy as sa
from datetime import datetime, timezone, timedelta
from ..filter.series.user_following import filter_user_following_query
from ..filter.series.user_can_watch import filter_user_can_watch_query
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/series-recently-aired')

@router.get('', response_model=schemas.Page_cursor_result[schemas.Series_and_episode])
async def get_series_recently_aired(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
    user_following: bool = Query(default=None),
    user_can_watch: bool = Query(default=None),
):
    dt = datetime.now(tz=timezone.utc)
    episodes_query = sa.select(
        models.Episode.series_id,
        sa.func.min(models.Episode.number).label('episode_number'),
    ).where(
        models.Series_follower.user_id == user.id,
        models.Episode.series_id == models.Series_follower.series_id,
        models.Episode.air_datetime > (dt-timedelta(days=7)),
        models.Episode.air_datetime < dt,        
        models.Series.id == models.Episode.series_id,
    ).group_by(models.Episode.series_id)
    
    if user_following != None:
        episodes_query = filter_user_following_query(episodes_query, user_following=user_following, user_id=user.id)
    if user_can_watch != None:
        episodes_query = filter_user_can_watch_query(episodes_query, user_id=user.id, episode_number=models.Episode.number)
    
    episodes_query = episodes_query.subquery()

    query = sa.select(models.Series, models.Episode).where(
        models.Series.id == episodes_query.c.series_id,
        models.Episode.series_id == models.Series.id,
        models.Episode.number == episodes_query.c.episode_number,
    ).order_by(
        sa.desc(models.Episode.air_datetime), 
        models.Episode.series_id,
    )

    p = await utils.sqlalchemy.paginate_cursor(session=session, query=query, page_query=page_query)
    p.items = [schemas.Series_and_episode(series=item.Series, episode=item.Episode) for item in p.items]
    return p