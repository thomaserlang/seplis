import sqlalchemy as sa
from fastapi import Depends, Security

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.post(
    '/{play_server_id}/invites',
    response_model=schemas.Play_server_invite_id,
    status_code=201,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def create_play_server_invite(
    play_server_id: str,
    data: schemas.Play_server_invite_create,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
):
    return await models.MPlayServerInvite.invite(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        data=data,
    )


@router.get(
    '/{play_server_id}/invites',
    response_model=schemas.Page_cursor_total_result[schemas.Play_server_invite],
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def get_play_server_invites(
    play_server_id: str,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
    session: AsyncSession = Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = (
        sa.select(
            models.MPlayServerInvite.created_at,
            models.MPlayServerInvite.expires_at,
            models.MUserPublic,
        )
        .where(
            models.MPlayServer.user_id == user.id,
            models.MPlayServer.id == play_server_id,
            models.MPlayServerInvite.play_server_id == models.MPlayServer.id,
            models.MUserPublic.id == models.MPlayServerInvite.user_id,
        )
        .order_by(sa.asc(models.MPlayServer.name))
    )

    p = await utils.sqlalchemy.paginate_cursor_total(
        session=session, query=query, page_query=page_query
    )
    p.items = [
        schemas.Play_server_invite(
            created_at=r.created_at,
            expires_at=r.expires_at,
            user=schemas.User_public.model_validate(r.MUserPublic),
        )
        for r in p.items
    ]
    return p


@router.post(
    '/accept-invite',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def accept_play_server_invite(
    data: schemas.Play_server_invite_id,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
) -> None:
    await models.MPlayServerInvite.accept_invite(
        user_id=user.id,
        invite_id=data.invite_id,
    )
