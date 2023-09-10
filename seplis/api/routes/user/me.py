from fastapi import Security, Depends
import sqlalchemy as sa
from starlette.concurrency import run_in_threadpool
from passlib.hash import pbkdf2_sha256
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas, exceptions
from .router import router


@router.get('/me', response_model=schemas.User,
            description='''
            **Scope required:** `user:read`
            ''')
async def get_user(
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:read']),
    session: AsyncSession = Depends(get_session),
) -> schemas.User:
    u = await session.scalar(sa.select(models.User).where(models.User.id == user.id))
    if not u:
        raise exceptions.Not_found('User not found')
    return schemas.User.model_validate(u)


@router.put('/me', response_model=schemas.User, status_code=200,
            description='''
            **Scope required:** `user:edit`
            ''')
async def update_user(
    user_data: schemas.User_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:edit']),
) -> schemas.User:
    return await models.User.save(user_data, user_id=user.id)


@router.post('/me/change-password', status_code=204,
            description='''
            **Scope required:** `me`
            ''')
async def change_password(
    data: schemas.User_change_password,
    user: schemas.User_authenticated = Security(authenticated, scopes=['me']),
    session: AsyncSession = Depends(get_session),
):
    password_hash = await session.scalar(sa.select(models.User.password).where(models.User.id == user.id))
    if not password_hash:
        raise exceptions.User_unknown()

    matches = await run_in_threadpool(pbkdf2_sha256.verify, data.current_password, password_hash)
    if not matches:
        raise exceptions.Wrong_password()
    await models.User.change_password(
        user_id=user.id,
        new_password=data.new_password,
        current_token=user.token,
    )