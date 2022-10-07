from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from httpx import AsyncClient
from .schemas import User_authenticated
from .database import database
from . import models, exceptions

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/1/token")

async def get_session() -> AsyncSession:
    async with database.session() as session:
        yield session

async def authenticated(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> User_authenticated:
    user = await models.Token.get(token)
    if not user:
        raise exceptions.Not_signed_in_exception()
    if user.level < int(security_scopes.scope_str):
        raise exceptions.Forbidden(
            f'Required user level {security_scopes.scope_str}'
        )
    return user

httpx_client = AsyncClient()