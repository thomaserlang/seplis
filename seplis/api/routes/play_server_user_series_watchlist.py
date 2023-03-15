from fastapi import Depends
import sqlalchemy as sa
from ..dependencies import get_session, AsyncSession
from .. import models, schemas
from ... import utils
from .play_server import router

@router.get('/{play_server_id}/user-series-watchlist', response_model=schemas.Page_cursor_result[schemas.Series])
async def get_play_servers_user_series_watchlist(
    play_server_id: str,
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = sa.select(models.Series).where(
        models.Play_server_access.play_server_id == play_server_id,
        models.Series_watchlist.user_id == models.Play_server_access.user_id,
        models.Series.id == models.Series_watchlist.series_id,
    ).order_by(models.Series.id).group_by(models.Series.id)

    p = await utils.sqlalchemy.paginate_cursor(session=session, query=query, page_query=page_query)
    p.items = [r.Series for r in p.items]
    return p
