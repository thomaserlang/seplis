import sqlalchemy as sa
from fastapi import Depends, Security

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get('', response_model=schemas.Page_cursor_total_result[schemas.Play_server],
            description='''
            **Scope required:** `user:list_play_servers`
            ''')
async def get_play_servers(
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:list_play_servers']),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = sa.select(models.MPlayServer).where(
        models.MPlayServer.user_id == user.id,
    ).order_by(sa.asc(models.MPlayServer.name))

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [row.Play_server for row in p.items]
    return p
