from fastapi import APIRouter, Depends, Query, Security
import sqlalchemy as sa
from datetime import datetime, timezone
from seplis.api.filter.series import filter_series_query

from seplis.api.filter.series.query_filter_schema import Series_query_filter
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .... import utils
from .router import router

@router.get('/to-watch', response_model=schemas.Page_cursor_total_result[schemas.Series_and_episode],
            description='''
            **Scope required:** `user:view_lists`
            ''')
async def get_user_series_to_watch(
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
    session: AsyncSession=Depends(get_session),
    page_cursor: schemas.Page_cursor_query = Depends(),
    filter_query: Series_query_filter = Depends()
):
    episodes_query = sa.select(
        models.Episode_watched.series_id,
        sa.func.max(models.Episode_watched.episode_number).label('episode_number'),
    ).where(
        models.Series_watchlist.user_id == user.id,
        models.Episode_watched.user_id == models.Series_watchlist.user_id,
        models.Episode_watched.series_id == models.Series_watchlist.series_id,
        models.Episode_watched.times > 0,
    ).group_by(models.Episode_watched.series_id).subquery()

    latest_aired_episode = sa.select(
        models.Episode.series_id,
        sa.func.max(models.Episode.air_datetime).label('latest_aired_episode_datetime'),
    ).where(
        models.Series_watchlist.user_id == user.id,
        models.Episode.series_id == models.Series_watchlist.series_id,
    ).group_by(models.Episode.series_id)
    
    if not filter_query.user_can_watch:
        latest_aired_episode = latest_aired_episode.where(
            models.Episode.air_datetime <= datetime.now(tz=timezone.utc),
        )

    latest_aired_episode = latest_aired_episode.subquery()
    

    query = sa.select(models.Series, models.Episode).where(
        models.Series.id == episodes_query.c.series_id,
        models.Episode.series_id == models.Series.id,
        models.Episode.number == episodes_query.c.episode_number+1,
        latest_aired_episode.c.series_id == models.Series.id,
    )

    if not filter_query.user_can_watch:
        query = query.where(
            models.Episode.air_datetime <= datetime.now(tz=timezone.utc),
        )

    query = filter_series_query(
        query=query,
        filter_query=filter_query,
        can_watch_episode_number=models.Episode.number,
    ).order_by(None).order_by(
        sa.desc(latest_aired_episode.c.latest_aired_episode_datetime),
        sa.desc(models.Series.popularity),
        models.Episode.series_id,
    )
    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_cursor)
    p.items = [schemas.Series_and_episode(series=item.Series, episode=item.Episode) for item in p.items]
    return p