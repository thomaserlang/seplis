from fastapi import APIRouter, Depends, Request
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas
from ... import utils, logger

router = APIRouter(prefix='/2/play-servers/{play_server_id}/user-movies-stared')

@router.get('', response_model=schemas.Page_result[schemas.Movie])
async def get_play_servers(
    play_server_id: str,
    request: Request,
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = sa.select(models.Movie).where(
        models.Play_server_access.play_server_id == play_server_id,
        models.Movie_stared.user_id == models.Play_server_access.user_id,
        models.Movie.id == models.Movie_stared.movie_id,
    ).order_by(models.Movie.id).group_by(models.Movie.id)

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    return p
