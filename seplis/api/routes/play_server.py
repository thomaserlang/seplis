from fastapi import APIRouter, Depends, Request, Security
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/play-servers')

@router.get('', response_model=schemas.Page_result[schemas.Play_server])
async def get_play_servers(
    request: Request,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = sa.select(models.Play_server).where(
        models.Play_server.user_id == user.id,
    ).order_by(sa.asc(models.Play_server.name))

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    return p


@router.post('', response_model=schemas.Play_server_with_secret)