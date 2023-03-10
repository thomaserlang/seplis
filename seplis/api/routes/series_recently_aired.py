from fastapi import APIRouter, Depends
import sqlalchemy as sa
from datetime import datetime, timezone, timedelta
from ..filter.series import filter_series_query
from ..filter.series.query_filter_schema import Series_query_filter
from ..dependencies import get_session, AsyncSession
from .. import models, schemas
from ... import utils

router = APIRouter(prefix='/2/series-recently-aired')

@router.get('', response_model=schemas.Page_cursor_result[schemas.Series_and_episode])
async def get_series_recently_aired(
    session: AsyncSession=Depends(get_session),
    page_cursor: schemas.Page_cursor_query = Depends(),
    filter_query: Series_query_filter = Depends(),
):
    dt = datetime.now(tz=timezone.utc)
    episodes_query = sa.select(
        models.Episode.series_id,
        sa.func.min(models.Episode.number).label('episode_number'),
    ).where(
        models.Episode.air_datetime > (dt-timedelta(days=7)),
        models.Episode.air_datetime < dt,        
        models.Series.id == models.Episode.series_id,
    ).group_by(models.Episode.series_id)
    
    episodes_query = filter_series_query(
        query=episodes_query,
        filter_query=filter_query,
        can_watch_episode_number=models.Episode.number,
    )
    episodes_query = episodes_query.subquery()

    query = sa.select(models.Series, models.Episode).where(
        models.Series.id == episodes_query.c.series_id,
        models.Episode.series_id == models.Series.id,
        models.Episode.number == episodes_query.c.episode_number,
    ).order_by(
        sa.desc(models.Episode.air_datetime), 
        models.Episode.series_id,
    )

    p = await utils.sqlalchemy.paginate_cursor(session=session, query=query, page_query=page_cursor)
    p.items = [schemas.Series_and_episode(series=item.Series, episode=item.Episode) for item in p.items]
    return p