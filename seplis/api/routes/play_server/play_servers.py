from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .... import utils
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
    query = sa.select(models.Play_server).where(
        models.Play_server.user_id == user.id,
    ).order_by(sa.asc(models.Play_server.name))

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [row.Play_server for row in p.items]
    return p
