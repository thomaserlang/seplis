from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
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
    if user.level < int(security_scopes.scope_str):
        raise exceptions.Forbidden(
            f'Required user level {security_scopes.scope_str}'
        )
    return user


async def get_expand(expand: str | None = None):
    if expand:
        return [e.strip() for e in expand.split(',')]


httpx_client = AsyncClient()