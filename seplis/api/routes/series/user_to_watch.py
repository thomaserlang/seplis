from datetime import UTC, datetime

import sqlalchemy as sa
from fastapi import Depends, Security

from seplis.api.filter.series import filter_series_query
from seplis.api.filter.series.query_filter_schema import Series_query_filter

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get(
    '/to-watch',
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def get_user_series_to_watch(
    user: User_authenticated = Security(authenticated, scopes=['user:view_lists']),
    session: AsyncSession = Depends(get_session),
    page_cursor: schemas.Page_cursor_query = Depends(),
    filter_query: Series_query_filter = Depends(),
) -> schemas.Page_cursor_result[schemas.Series_and_episode]:
    episodes_query = (
        sa.select(
            models.MEpisodeWatched.series_id,
            sa.func.max(models.MEpisodeWatched.episode_number).label('episode_number'),
        )
        .where(
            models.MSeriesWatchlist.user_id == user.id,
            models.MEpisodeWatched.user_id == models.MSeriesWatchlist.user_id,
            models.MEpisodeWatched.series_id == models.MSeriesWatchlist.series_id,
            models.MEpisodeWatched.times > 0,
        )
        .group_by(models.MEpisodeWatched.series_id)
        .subquery()
    )

    latest_aired_episode = (
        sa.select(
            models.MEpisode.series_id,
            sa.func.max(models.MEpisode.air_datetime).label(
                'latest_aired_episode_datetime'
            ),
        )
        .where(
            models.MSeriesWatchlist.user_id == user.id,
            models.MEpisode.series_id == models.MSeriesWatchlist.series_id,
            models.MEpisode.air_datetime <= datetime.now(tz=UTC),
        )
        .group_by(models.MEpisode.series_id)
        .subquery()
    )

    query = sa.select(models.MSeries, models.MEpisode).where(
        models.MSeries.id == episodes_query.c.series_id,
        models.MEpisode.series_id == models.MSeries.id,
        models.MEpisode.number == episodes_query.c.episode_number + 1,
        models.MEpisode.air_datetime <= datetime.now(tz=UTC),
        latest_aired_episode.c.series_id == models.MSeries.id,
    )

    query = (
        filter_series_query(
            query=query,
            filter_query=filter_query,
            can_watch_episode_number=models.MEpisode.number,
        )
        .order_by(None)
        .order_by(
            sa.desc(latest_aired_episode.c.latest_aired_episode_datetime),
            sa.desc(sa.func.coalesce(models.MSeries.popularity, 0)),
            models.MEpisode.series_id,
        )
    )
    p = await utils.sqlalchemy.paginate_cursor_total(
        session=session, query=query, page_query=page_cursor
    )
    p.items = [
        schemas.Series_and_episode(series=item.MSeries, episode=item.MEpisode)
        for item in p.items
    ]
    return p
