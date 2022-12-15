from fastapi import APIRouter, Depends, Request, Security
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions
from ... import utils, logger

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


@router.post('', response_model=schemas.Play_server_with_url, status_code=201)
async def create_play_server(
    data: schemas.Play_server_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    p = await models.Play_server.save(data=data, id_=None, user_id=user.id)
    return p


@router.put('/{play_server_id}', response_model=schemas.Play_server_with_url)
async def update_play_server(
    play_server_id: int | str,
    data: schemas.Play_server_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    p = await models.Play_server.save(data=data, id_=play_server_id, user_id=user.id)
    return p


@router.get('/{play_server_id}', response_model=schemas.Play_server_with_url)
async def get_play_server(
    play_server_id: int | str,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
):
    p = await session.scalar(sa.select(models.Play_server).where(
        models.Play_server.user_id == user.id,
        models.Play_server.id == play_server_id,
    ))
    if not p:
        raise exceptions.Not_found('Unknown play server')
    return p


@router.delete('/{play_server_id}', status_code=204)
async def delete_play_server(
    play_server_id: int | str,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await models.Play_server.delete(id_=play_server_id, user_id=user.id)


@router.post('/{play_server_id}/invites', response_model=schemas.Play_server_invite_id, status_code=201)
async def create_play_server_invite(
    play_server_id: str,
    data: schemas.Play_server_invite_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    p = await models.Play_server_invite.invite(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        data=data,
    )
    return p


@router.get('/{play_server_id}/invites', response_model=schemas.Page_result[schemas.Play_server_invite])
async def get_play_server_invites(
    play_server_id: str,
    request: Request,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = sa.select(models.Play_server_invite.created_at, models.Play_server_invite.expires_at, models.User_public).where(
        models.Play_server.user_id == user.id,
        models.Play_server.id == play_server_id,
        models.Play_server_invite.play_server_id == models.Play_server.id,
        models.User_public.id == models.Play_server_invite.user_id,
    ).order_by(sa.asc(models.Play_server.name))

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request, scalars=False)
    p.items = [schemas.Play_server_invite(
        created_at=r.created_at,
        expires_at=r.expires_at,
        user=schemas.User_public.from_orm(r.User_public)) for r in p.items]
    return p


@router.get('/{play_server_id}/access', response_model=schemas.Page_result[schemas.Play_server_access])
async def get_play_server_access(
    play_server_id: str,
    request: Request,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = sa.select(models.Play_server_access.created_at, models.User_public).where(
        models.Play_server.user_id == user.id,
        models.Play_server.id == play_server_id,
        models.Play_server_access.play_server_id == models.Play_server.id,
        models.User_public.id == models.Play_server_access.user_id,
    ).order_by(sa.asc(models.User_public.username), sa.asc(models.User_public.id))

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request, scalars=False)
    p.items = [schemas.Play_server_access(
        created_at=r.created_at,
        user=schemas.User_public.from_orm(r.User_public)) for r in p.items]
    return p


@router.delete('/{play_server_id}/acceess/{user_id}', status_code=204)
async def remove_play_server_access(
    play_server_id: str,
    user_id: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await models.Play_server_access.remove_user(
        play_server_id=play_server_id,
        owner_user_id=user.id,
        user_id=user_id,
    )