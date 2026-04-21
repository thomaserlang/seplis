import sqlalchemy as sa
from fastapi import Depends, Security
from passlib.hash import pbkdf2_sha256
from starlette.concurrency import run_in_threadpool

from seplis.api.user import (
    User,
    UserChangePassword,
    UserUpdate,
    change_password,
    get_user,
    update_user,
)
from seplis.api.user.models.user_model import MUser

from ... import exceptions
from ...dependencies import AsyncSession, UserAuthenticated, authenticated, get_session
from .router import router


@router.get(
    '/me',
    response_model=User,
    description="""
            **Scope required:** `user:read`
            """,
)
async def get_user_route(
    user: UserAuthenticated = Security(authenticated, scopes=['user:read']),
    session: AsyncSession = Depends(get_session),
) -> User:
    u = await get_user(user_id=user.id, session=session)
    if not u:
        raise exceptions.Not_found('User not found')
    return u


@router.put(
    '/me',
    response_model=User,
    status_code=200,
    description="""
            **Scope required:** `user:edit`
            """,
)
async def update_user_route(
    user_data: UserUpdate,
    user: UserAuthenticated = Security(authenticated, scopes=['user:edit']),
) -> User:
    return await update_user(data=user_data, user_id=user.id)


@router.post(
    '/me/change-password',
    status_code=204,
    description="""
            **Scope required:** `me`
            """,
)
async def change_password_route(
    data: UserChangePassword,
    user: UserAuthenticated = Security(authenticated, scopes=['me']),
    session: AsyncSession = Depends(get_session),
) -> None:
    password_hash = await session.scalar(
        sa.select(MUser.password).where(MUser.id == user.id)
    )
    if not password_hash:
        raise exceptions.User_unknown()

    matches = await run_in_threadpool(
        pbkdf2_sha256.verify, data.current_password, password_hash
    )
    if not matches:
        raise exceptions.Wrong_password()
    await change_password(
        user_id=user.id,
        new_password=data.new_password,
        current_token=user.token,
    )
