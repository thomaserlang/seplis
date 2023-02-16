from fastapi import APIRouter, Depends, Request, Security
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions
from ... import utils

router = APIRouter(prefix='/2/play-servers')

@router.get('', response_model=schemas.Page_cursor_total_result[schemas.Play_server])
async def get_play_servers(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = sa.select(models.Play_server).where(
        models.Play_server.user_id == user.id,
    ).order_by(sa.asc(models.Play_server.name))

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [row.Play_server for row in p.items]
    return p


@router.post('', response_model=schemas.Play_server_with_url, status_code=201)
async def create_play_server(
    data: schemas.Play_server_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    p = await models.Play_server.save(data=data, play_server_id=None, user_id=user.id)
    return p


@router.put('/{play_server_id}', response_model=schemas.Play_server_with_url)
async def update_play_server(
    play_server_id: int | str,
    data: schemas.Play_server_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    p = await models.Play_server.save(data=data, play_server_id=play_server_id, user_id=user.id)
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


@router.get('/{play_server_id}/invites', response_model=schemas.Page_cursor_total_result[schemas.Play_server_invite])
async def get_play_server_invites(
    play_server_id: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
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
        user=schemas.User_public.from_orm(r.User_public)) for r in p.items]
    return p


@router.get('/{play_server_id}/access', response_model=schemas.Page_cursor_total_result[schemas.Play_server_access])
async def get_play_server_access(
    play_server_id: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
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


class Play_server_secret(SecurityBase):

    def __init__(self):
        from fastapi.openapi.models import SecurityBase, SecuritySchemeType
        self.model = SecurityBase(description='Add secret to authorization header', type=SecuritySchemeType.apiKey)
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request) -> str | None:
        authorization: str = request.headers.get('Authorization')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "secret":
            raise exceptions.Forbidden('Missing play server secret in authorization')
        return param
play_server_secret = Play_server_secret()


@router.put('/{play_server_id}/movies', status_code=204)
async def register_play_server_movies_put(
    play_server_id: str,
    data: list[schemas.Play_server_movie_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_movie.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=False,
    )


@router.patch('/{play_server_id}/movies', status_code=204)
async def register_play_server_movie_patch(
    play_server_id: str,
    data: list[schemas.Play_server_movie_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_movie.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=True,
    )


@router.delete('/{play_server_id}/movies/{movie_id}', status_code=204)
async def delete_movie_from_play_server(
    play_server_id: str,
    movie_id: int,
    secret: str = Security(play_server_secret),
):
    await models.Play_server_movie.delete(
        play_server_id=play_server_id,
        movie_id=movie_id,
        play_server_secret=secret,
    )


@router.put('/{play_server_id}/episodes', status_code=204)
async def register_play_server_episode_put(
    play_server_id: str,
    data: list[schemas.Play_server_episode_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_episode.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=False,
    )


@router.patch('/{play_server_id}/episodes', status_code=204)
async def register_play_server_episode_patch(
    play_server_id: str,
    data: list[schemas.Play_server_episode_create],
    secret: str = Security(play_server_secret),
):
    await models.Play_server_episode.save(
        play_server_id=play_server_id,
        play_server_secret=secret,
        data=data,
        patch=True,
    )


@router.delete('/{play_server_id}/series/{series_id}/episodes/{episode_number}', status_code=204)
async def delete_episode_from_play_server(
    play_server_id: str,
    series_id: int,
    episode_number: int,
    secret: str = Security(play_server_secret),
):
    await models.Play_server_episode.delete(
        play_server_id=play_server_id,
        series_id=series_id,
        episode_number=episode_number,
        play_server_secret=secret,
    )