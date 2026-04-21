import sqlalchemy as sa
from fastapi import Depends, Security

from seplis.api.user.models.user_model import MUserPublic

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get(
    '/access',
    response_model=schemas.Page_cursor_total_result[schemas.Play_server_with_url],
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def get_play_servers_with_access(
    user: User_authenticated = Security(authenticated, scopes=['user:list_play_servers']),
    session: AsyncSession = Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = (
        sa.select(models.MPlayServer)
        .where(
            models.MPlayServerAccess.user_id == user.id,
            models.MPlayServerAccess.play_server_id == models.MPlayServer.id,
            models.MPlayServer.user_id != user.id,
        )
        .order_by(sa.asc(models.MPlayServer.name), sa.asc(models.MPlayServer.id))
    )

    p = await utils.sqlalchemy.paginate_cursor_total(
        session=session, query=query, page_query=page_query
    )
    p.items = [row.Play_server for row in p.items]
    return p


@router.get(
    '/{play_server_id}/access',
    response_model=schemas.Page_cursor_total_result[schemas.Play_server_access],
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def get_users_with_access(
    play_server_id: str,
    user: User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
    session: AsyncSession = Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = (
        sa.select(models.MPlayServerAccess.created_at, MUserPublic)
        .where(
            models.MPlayServer.user_id == user.id,
            models.MPlayServer.id == play_server_id,
            models.MPlayServerAccess.play_server_id == models.MPlayServer.id,
            MUserPublic.id == models.MPlayServerAccess.user_id,
        )
        .order_by(sa.asc(MUserPublic.username), sa.asc(MUserPublic.id))
    )

    p = await utils.sqlalchemy.paginate_cursor_total(
        session=session, query=query, page_query=page_query
    )
    p.items = [
        schemas.Play_server_access(
            created_at=r.created_at,
            user=schemas.UserPublic.model_validate(r.MUserPublic),
        )
        for r in p.items
    ]
    return p


@router.delete(
    '/{play_server_id}/acceess/{user_id}',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def remove_user_access(
    play_server_id: str,
    user_id: str,
    user: User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
) -> None:
    await models.MPlayServerAccess.remove_user(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        user_id=user_id,
    )


@router.delete(
    '/{play_server_id}/access/me',
    status_code=204,
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def leave_play_server(
    play_server_id: str,
    user: User_authenticated = Security(authenticated, scopes=['user:list_play_servers']),
) -> None:
    await models.MPlayServerAccess.leave(
        play_server_id=play_server_id,
        user_id=user.id,
    )
