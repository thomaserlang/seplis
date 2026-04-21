from datetime import datetime
from typing import Literal

import sqlalchemy as sa
from fastapi import Depends
from pydantic import BaseModel

from ... import models, schemas
from ...dependencies import AsyncSession, get_session
from ...filter.series import filter_series, filter_series_query
from ...filter.series.query_filter_schema import Series_query_filter
from .play_server import router


class Sonarr_response(BaseModel):
    TvdbId: int


@router.get(
    '/{play_server_id}/users-series-watchlist',
    response_model=schemas.Page_cursor_result[schemas.Series] | list[Sonarr_response],
)
async def get_play_servers_user_series_watchlist(
    play_server_id: str,
    session: AsyncSession = Depends(get_session),
    page_cursor: schemas.Page_cursor_query = Depends(),
    filter_query: Series_query_filter = Depends(),
    added_at_ge: datetime = None,
    added_at_le: datetime = None,
    response_format: Literal['standard', 'sonarr'] = 'standard',
):
    query = (
        sa.select(models.MSeries)
        .where(
            models.MPlayServerAccess.play_server_id == play_server_id,
            models.MSeriesWatchlist.user_id == models.MPlayServerAccess.user_id,
            models.MSeries.id == models.MSeriesWatchlist.series_id,
        )
        .group_by(models.MSeries.id)
    )

    if added_at_ge:
        query = query.where(
            models.MSeriesWatchlist.created_at >= added_at_ge,
        )

    if added_at_le:
        query = query.where(
            models.MSeriesWatchlist.created_at <= added_at_le,
        )

    if response_format == 'standard':
        return await filter_series(
            query=query,
            session=session,
            filter_query=filter_query,
            page_cursor=page_cursor,
        )

    if response_format == 'sonarr':
        query = filter_series_query(query=query, filter_query=filter_query)
        rows = await session.scalars(query)
        return [
            Sonarr_response(TvdbId=int(r.externals['thetvdb']))
            for r in rows
            if r.externals.get('thetvdb')
        ]
    return None
