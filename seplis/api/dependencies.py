from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from httpx import AsyncClient
from .schemas import User_authenticated
from .database import database
from . import exceptions
from .. import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/2/token")

async def get_session() -> AsyncSession:
    async with database.session() as session:
        yield session


async def _check_token(token: str, security_scopes: SecurityScopes):
    from .models.user import Token
    user = await Token.get(token)
    if not user:
        raise exceptions.Not_signed_in_exception()
    if user.level < int(security_scopes.scope_str):
        raise exceptions.Forbidden(
            f'Required user level {security_scopes.scope_str}'
        )
    return user


async def authenticated(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    return await _check_token(token=token, security_scopes=security_scopes)


async def authenticated_if_expand(
    security_scopes: SecurityScopes, 
    token: str = Depends(oauth2_scheme),
    expand: str | None = None, 
) -> User_authenticated:
    if expand:
        return await _check_token(token=token, security_scopes=security_scopes)


async def get_expand(expand: str | None = None):
    if expand:
        return [e.strip() for e in expand.split(',')]


httpx_client = AsyncClient()