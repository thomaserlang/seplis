from fastapi import APIRouter, Security, Depends
import sqlalchemy as sa
from starlette.concurrency import run_in_threadpool
from passlib.hash import pbkdf2_sha256
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions
from ... import logger

router = APIRouter(prefix='/1/users')

@router.post('', response_model=schemas.User, status_code=201)
async def create_user(user_data: schemas.User_create) -> schemas.User_basic:
    return await models.User.save(user_data)


@router.get('/me', response_model=schemas.User)
async def get_user(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession = Depends(get_session),
) -> schemas.User:
    u = await session.scalar(sa.select(models.User).where(models.User.id == user.id))
    if not u:
        raise exceptions.Not_found('User not found')
    return schemas.User.from_orm(u)

@router.put('/me', response_model=schemas.User, status_code=200)
async def update_user(
    user_data: schemas.User_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
) -> schemas.User:
    return await models.User.save(user_data, user_id=user.id)


@router.post('/me/change-password', status_code=204)
async def change_password(
    data: schemas.User_change_password,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession = Depends(get_session),
):
    password = await session.scalar(sa.select(models.User.password).where(models.User.id == user.id))
    if not password:
        raise exceptions.User_unknown()
    matches = await run_in_threadpool(pbkdf2_sha256.verify, data.current_password, password)
    if not matches:
        raise exceptions.Wrong_password()
    logger.error(user.token)
    await models.User.change_password(
        user_id=user.id,
        new_password=data.new_password,
        current_token=user.token,
    )


@router.get('', response_model=list[schemas.User_public])
async def get_users(
    username: str,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession = Depends(get_session),
):
    users = await session.scalars(sa.select(models.User).where(models.User.username == username))
    return [schemas.User_public.from_orm(u) for u in users]