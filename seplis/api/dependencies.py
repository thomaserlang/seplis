from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from . import exceptions
from .database import database
from .user import UserAuthenticated
from .user.actions.token_actions import get_authenticated_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/2/token')
oauth2_scheme_no_raise = OAuth2PasswordBearer(tokenUrl='/2/token', auto_error=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with database.session() as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserAuthenticated:
    user = await get_authenticated_user(token)
    if not user:
        raise exceptions.Not_signed_in_exception()
    return user


async def get_current_user_no_raise(
    token: Annotated[str, Depends(oauth2_scheme_no_raise)],
) -> UserAuthenticated | None:
    return await get_authenticated_user(token)


async def authenticated(
    security_scopes: SecurityScopes,
    user: Annotated[UserAuthenticated, Depends(get_current_user)],
) -> UserAuthenticated:
    for scope in security_scopes.scopes:
        if user.scopes and scope in user.scopes:
            break
    else:
        raise exceptions.Forbidden(
            f'Required scope(s): {", ".join(security_scopes.scopes)}'
        )
    return user


async def get_expand(expand: str | None = None) -> list[str] | None:
    if expand:
        return [e.strip() for e in expand.split(',')]
    return None


class Play_server_secret(SecurityBase):
    def __init__(self) -> None:
        from fastapi.openapi.models import SecurityBase, SecuritySchemeType

        self.model = SecurityBase(
            description='Add secret to authorization header',
            type=SecuritySchemeType.apiKey,
        )
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request) -> str | None:
        authorization: str | None = request.headers.get('Authorization')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'secret':
            raise exceptions.Forbidden('Missing play server secret in authorization')
        return param


play_server_secret = Play_server_secret()


httpx_client = AsyncClient()
