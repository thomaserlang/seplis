from fastapi import APIRouter, Depends, Request
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas
from ... import utils, logger

router = APIRouter(prefix='/2/play-servers/{play_server_id}/user-series-following')


@router.get('', response_model=schemas.Page_result[schemas.Series])
async def get_series_following(
    play_server_id: str,
    request: Request,
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = sa.select(models.Series).where(
        models.Play_server_access.play_server_id == play_server_id,
        models.Series_follower.user_id == models.Play_server_access.user_id,
        models.Series.id == models.Series_follower.series_id,
    ).order_by(models.Series.id).group_by(models.Series.id)

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    return p
