from fastapi import APIRouter, Body, Depends, Query, Security
import sqlalchemy as sa
from datetime import datetime, timezone
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/series-to-watch')

@router.get('', response_model=schemas.Page_cursor_total_result[schemas.Series_and_episode])
async def get_user_series_to_watch(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_cursor: schemas.Page_cursor_query = Depends(),
    user_can_watch: bool | None = Query(None)
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
        models.Series.id == episodes_query.c.series_id,
        models.Episode.series_id == models.Series.id,
        models.Episode.number == episodes_query.c.episode_number+1,
        models.Episode.air_datetime <= datetime.now(tz=timezone.utc),
    ).order_by(
        sa.desc(models.Episode.air_datetime), 
        models.Episode.series_id,
    )

    if user_can_watch:
        query = query.where(
            models.Play_server_access.user_id == user.id,
            models.Play_server_episode.play_server_id == models.Play_server_access.play_server_id,
            models.Play_server_episode.series_id == models.Episode.series_id,
            models.Play_server_episode.episode_number == models.Episode.number,            
        )
    

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_cursor)
    p.items = [schemas.Series_and_episode(series=item.Series, episode=item.Episode) for item in p.items]
    return p