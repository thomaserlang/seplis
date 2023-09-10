from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .... import utils
from .router import router


@router.get('/{play_server_id}/access', 
            response_model=schemas.Page_cursor_total_result[schemas.Play_server_access],
            description='''
            **Scope required:** `user:manage_play_servers`
            ''')
async def get_users_with_access(
    play_server_id: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_servers']),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = sa.select(models.Play_server_access.created_at, models.User_public).where(
        models.Play_server.user_id == user.id,
        models.Play_server.id == play_server_id,
        models.Play_server_access.play_server_id == models.Play_server.id,
        models.User_public.id == models.Play_server_access.user_id,
    ).order_by(sa.asc(models.User_public.username), sa.asc(models.User_public.id))

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [schemas.Play_server_access(
        created_at=r.created_at,
        user=schemas.User_public.model_validate(r.User_public)) for r in p.items]
    return p


@router.delete('/{play_server_id}/acceess/{user_id}', status_code=204,
            description='''
            **Scope required:** `user:manage_play_servers`
            ''')
async def remove_user_access(
    play_server_id: str,
    user_id: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_servers']),
):
    await models.Play_server_access.remove_user(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        user_id=user_id,
    )