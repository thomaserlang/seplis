from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from httpx import AsyncClient
from .database import database
from .models.user import Token
from . import exceptions
from .schemas.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/2/token")
oauth2_scheme_no_raise = OAuth2PasswordBearer(tokenUrl="/2/token", auto_error=False)


async def get_session() -> AsyncSession:
    async with database.session() as session:
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await Token.get(token)
    if not user:
        raise exceptions.Not_signed_in_exception()
    return user


async def get_current_user_no_raise(token: str = Depends(oauth2_scheme_no_raise)):
    return await Token.get(token)


async def authenticated(
    security_scopes: SecurityScopes, 
    user: User = Depends(get_current_user),
):
    for scope in security_scopes.scopes:
        if scope in user.scopes:
            break
    else:
        raise exceptions.Forbidden(
            f'Required scope(s): {", ".join(security_scopes.scopes)}'
        )
    return user
  

async def get_expand(expand: str | None = None):
    if expand:
        return [e.strip() for e in expand.split(',')]


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


httpx_client = AsyncClient()