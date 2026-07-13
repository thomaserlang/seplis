from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api import exceptions
from seplis.api.dependencies import authenticated

from ..actions.user_actions import change_own_password, get_user, update_user
from ..schemas.user_authentication_schemas import UserAuthenticated, UserChangePassword
from ..schemas.user_schemas import User, UserUpdate

router = APIRouter(prefix='/users')


@router.get(
    '/me', description='\n            **Scope required:** `user:read`\n            '
)
async def get_user_route(
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:read'])],
) -> User:
    current_user = await get_user(user_id=user.id)
    if not current_user:
        raise exceptions.NotFound('User not found')
    return current_user


@router.put(
    '/me',
    status_code=200,
    description="""
            **Scope required:** `user:edit`
            """,
)
async def update_user_route(
    user_data: UserUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:edit'])],
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
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['me'])],
) -> None:
    await change_own_password(user_id=user.id, data=data, current_token=user.token)
