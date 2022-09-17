from fastapi import APIRouter, Security, Depends
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession, httpx_client
from ..database import database
from .. import models, schemas, constants, exceptions
from ... import logger, utils, config

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
async def change_password(data: schemas.User_change_password):
    await models.User.change_password()