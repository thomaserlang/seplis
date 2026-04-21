import sqlalchemy as sa
from fastapi import Depends, Security

from ... import exceptions, models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.post(
    '',
    response_model=schemas.Play_server_with_url,
    status_code=201,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def create_play_server(
    data: schemas.Play_server_create,
    user: User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
):
    return await models.MPlayServer.save(data=data, play_server_id=None, user_id=user.id)


@router.put(
    '/{play_server_id}',
    response_model=schemas.Play_server_with_url,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def update_play_server(
    play_server_id: int | str,
    data: schemas.Play_server_update,
    user: User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
):
    return await models.MPlayServer.save(
        data=data, play_server_id=play_server_id, user_id=user.id
    )


@router.get(
    '/{play_server_id}',
    response_model=schemas.Play_server_with_url,
    description="""
            **Scope required:** `user:list_play_servers`
            """,
)
async def get_play_server(
    play_server_id: int | str,
    user: User_authenticated = Security(authenticated, scopes=['user:list_play_servers']),
    session: AsyncSession = Depends(get_session),
):
    p = await session.scalar(
        sa.select(models.MPlayServer).where(
            models.MPlayServer.user_id == user.id,
            models.MPlayServer.id == play_server_id,
        )
    )
    if not p:
        raise exceptions.Not_found('Unknown play server')
    return p


@router.delete(
    '/{play_server_id}',
    status_code=204,
    description="""
            **Scope required:** `user:manage_play_servers`
            """,
)
async def delete_play_server(
    play_server_id: int | str,
    user: User_authenticated = Security(
        authenticated, scopes=['user:manage_play_servers']
    ),
) -> None:
    await models.MPlayServer.delete(id_=play_server_id, user_id=user.id)
