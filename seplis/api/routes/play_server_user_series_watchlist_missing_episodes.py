from datetime import datetime, timezone
from fastapi import Depends
import sqlalchemy as sa
from ..dependencies import get_session, AsyncSession
from .. import models, schemas
from ... import utils
from .play_server import router


@router.get('/{play_server_id}/user-series-watchlist-missing-episodes', response_model=schemas.Page_cursor_result[schemas.Series])
async def get_play_server_series_watchlist_missing_episodes(
    play_server_id: str,
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    series_query = sa.select(models.Play_server_episode.series_id).where(
        models.Play_server_episode.play_server_id == play_server_id,
    ).group_by(models.Play_server_episode.series_id).subquery()

    query = sa.select(models.Series, models.Episode.number).where(
        models.Episode.series_id == series_query.c.series_id,
    ).join(models.Play_server_episode, sa.and_(
        models.Play_server_episode.series_id == models.Episode.series_id,
        models.Play_server_episode.episode_number == models.Episode.number,
        models.Play_server_episode.play_server_id == play_server_id,
    ), isouter=True).where(
        models.Play_server_episode.episode_number == None,
        models.Episode.air_datetime <= datetime.now(tz=timezone.utc),
        models.Series.id == models.Episode.series_id,
        models.Play_server_access.play_server_id == play_server_id,
        models.Series_watchlist.user_id == models.Play_server_access.user_id,
        models.Series_watchlist.series_id == models.Series.id,
    ).group_by(
        models.Episode.series_id,
    ).order_by(models.Series.id)

    p = await utils.sqlalchemy.paginate_cursor(session=session, query=query, page_query=page_query)
    p.items = [r.Series for r in p.items]
    return p
