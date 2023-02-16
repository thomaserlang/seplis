from fastapi import APIRouter, Depends, Security
import sqlalchemy as sa
from datetime import datetime, timezone
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/series-countdown')

@router.get('', response_model=schemas.Page_cursor_result[schemas.Series_and_episode])
async def get_series_recently_aired(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    episodes_query = sa.select(
        models.Episode.series_id,
        sa.func.min(models.Episode.number).label('episode_number'),
    ).where(
        models.Series_follower.user_id == user.id,
        models.Episode.series_id == models.Series_follower.series_id,
        models.Episode.air_datetime > datetime.now(tz=timezone.utc),
    ).group_by(models.Episode.series_id).subquery()
    query = sa.select(models.Series, models.Episode).where(
        models.Series.id == episodes_query.c.series_id,
        models.Episode.series_id == models.Series.id,
        models.Episode.number == episodes_query.c.episode_number,
    ).order_by(
        sa.asc(models.Episode.air_datetime), 
        models.Episode.series_id,
    )

    p = await utils.sqlalchemy.paginate_cursor(session=session, query=query, page_query=page_query)
    p.items = [schemas.Series_and_episode(series=item.Series, episode=item.Episode) for item in p.items]
    return p