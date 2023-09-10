from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .... import utils
from .router import router


@router.post('/{play_server_id}/invites', response_model=schemas.Play_server_invite_id, status_code=201,
            description='''
            **Scope required:** `user:manage_play_servers`
            ''')
async def create_play_server_invite(
    play_server_id: str,
    data: schemas.Play_server_invite_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_servers']),
):
    p = await models.Play_server_invite.invite(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        data=data,
    )
    return p


@router.get('/{play_server_id}/invites', 
            response_model=schemas.Page_cursor_total_result[schemas.Play_server_invite],
            description='''
            **Scope required:** `user:manage_play_servers`
            ''')
async def get_play_server_invites(
    play_server_id: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_servers']),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = sa.select(models.Play_server_invite.created_at, models.Play_server_invite.expires_at, models.User_public).where(
        models.Play_server.user_id == user.id,
        models.Play_server.id == play_server_id,
        models.Play_server_invite.play_server_id == models.Play_server.id,
        models.User_public.id == models.Play_server_invite.user_id,
    ).order_by(sa.asc(models.Play_server.name))

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [schemas.Play_server_invite(
        created_at=r.created_at,
        expires_at=r.expires_at,
        user=schemas.User_public.model_validate(r.User_public)) for r in p.items]
    return p


@router.post('/accept-invite', status_code=204,
            description='''
            **Scope required:** `user:manage_play_servers`
            ''')
async def accept_play_server_invite(
    data: schemas.Play_server_invite_id,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_servers']),
):
    await models.Play_server_invite.accept_invite(
        user_id=user.id,
        invite_id=data.invite_id,
    )