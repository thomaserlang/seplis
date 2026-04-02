from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from fastapi import Depends
from pydantic import conint

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, get_session
from ...filter.series import filter_series_query
from ...filter.series.query_filter_schema import Series_query_filter
from .router import router


@router.get(
    '/recently-aired',
    response_model=schemas.Page_cursor_result[schemas.Series_and_episode],
)
async def get_series_recently_aired(
    session: AsyncSession = Depends(get_session),
    page_cursor: schemas.Page_cursor_query = Depends(),
    filter_query: Series_query_filter = Depends(),
    days_ahead: conint(ge=0, le=10) = 0,
    days_behind: conint(ge=0, le=10) = 7,
):
    dt = datetime.now(tz=UTC)
    episodes_query = (
        sa.select(
            models.MEpisode.series_id,
            sa.func.min(models.MEpisode.number).label('episode_number'),
        )
        .where(
            models.MEpisode.air_datetime > (dt - timedelta(days=days_behind)),
            models.MEpisode.air_datetime < (dt + timedelta(days=days_ahead)),
            models.MSeries.id == models.MEpisode.series_id,
        )
        .group_by(models.MEpisode.series_id)
    )

    episodes_query = filter_series_query(
        query=episodes_query,
        filter_query=filter_query,
        can_watch_episode_number=models.MEpisode.number,
    )
    episodes_query = episodes_query.subquery()

    query = (
        sa.select(models.MSeries, models.MEpisode)
        .where(
            models.MSeries.id == episodes_query.c.series_id,
            models.MEpisode.series_id == models.MSeries.id,
            models.MEpisode.number == episodes_query.c.episode_number,
        )
        .order_by(
            sa.desc(models.MEpisode.air_datetime),
            models.MEpisode.series_id,
        )
    )

    p = await utils.sqlalchemy.paginate_cursor(
        session=session, query=query, page_query=page_cursor
    )
    p.items = [
        schemas.Series_and_episode(series=item.MSeries, episode=item.MEpisode)
        for item in p.items
    ]
    return p
