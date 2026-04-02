from datetime import UTC, datetime

import sqlalchemy as sa
from fastapi import Depends, Security

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get(
    '/countdown',
    response_model=schemas.Page_cursor_result[schemas.Series_and_episode],
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def series_countdown(
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['user:view_lists']
    ),
    session: AsyncSession = Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    episodes_query = (
        sa.select(
            models.MEpisode.series_id,
            sa.func.min(models.MEpisode.number).label('episode_number'),
        )
        .where(
            models.MSeriesWatchlist.user_id == user.id,
            models.MEpisode.series_id == models.MSeriesWatchlist.series_id,
            models.MEpisode.air_datetime > datetime.now(tz=UTC),
        )
        .group_by(models.MEpisode.series_id)
        .subquery()
    )
    query = (
        sa.select(models.MSeries, models.MEpisode)
        .where(
            models.MSeries.id == episodes_query.c.series_id,
            models.MEpisode.series_id == models.MSeries.id,
            models.MEpisode.number == episodes_query.c.episode_number,
        )
        .order_by(
            sa.asc(sa.func.coalesce(models.MEpisode.air_datetime, '1970-01-01 00:00:00')),
            models.MEpisode.series_id,
        )
    )

    p = await utils.sqlalchemy.paginate_cursor(
        session=session, query=query, page_query=page_query
    )
    p.items = [
        schemas.Series_and_episode(series=item.MSeries, episode=item.MEpisode)
        for item in p.items
    ]
    return p
