from datetime import UTC, datetime, timedelta
from typing import Any, cast

import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256  # ty: ignore[unresolved-import]
from redis.asyncio.client import Pipeline
from starlette.concurrency import run_in_threadpool

from seplis import utils
from seplis.api import constants, exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.database import database

from ..models.token_model import MToken
from ..models.user_model import MUser
from ..schemas.user_authentication_schemas import Token, TokenCreate, UserAuthenticated


async def create_token(
    user_id: int,
    scopes: list[str] | str,
    app_id: int | None = None,
    expires_days: int = constants.USER_TOKEN_EXPIRE_DAYS,
) -> str:
    if isinstance(scopes, str):
        scopes = scopes.split(' ')
    async with database.session() as session:
        token = utils.random_key(256)
        await session.execute(
            sa.insert(MToken.__table__).values(  # type: ignore
                app_id=app_id,
                user_id=user_id,
                expires=datetime.now(tz=UTC) + timedelta(days=expires_days),
                token=token,
                scopes=' '.join(scopes),
            )
        )
        await session.commit()
        p = cast(Pipeline, database.redis.pipeline())
        cache_token(p, token, user_id, scopes)
        await p.execute()
        return token


async def create_login_token(
    data: TokenCreate, session: AsyncSession | None = None
) -> Token:
    async with get_session(session) as session:
        user = await session.scalar(
            sa.select(MUser).where(
                sa.or_(
                    MUser.email == data['login'],
                    MUser.username == data['login'],
                )
            )
        )

        if not user:
            raise exceptions.WrongLoginOrPassword()

        try:
            matches = await run_in_threadpool(
                pbkdf2_sha256.verify, data['password'], user.password if user else ''
            )
        except Exception:
            matches = False
        if not matches:
            raise exceptions.WrongLoginOrPassword()

        token = await create_token(user_id=user.id, scopes=user.scopes)
        return Token(access_token=token)


async def create_progress_token(user_id: int) -> Token:
    token = await create_token(user_id=user_id, scopes=['user:progress'], expires_days=1)
    return Token(access_token=token)


async def get_authenticated_user(token: str) -> UserAuthenticated | None:
    r = await cast(Any, database.redis.hgetall(f'seplis:tokens:{token}:user'))
    if r:
        r['scopes'] = r['scopes'].split(' ') if r.get('scopes') else ['me']
        if 'me' in r['scopes']:
            r['scopes'].extend(constants.SCOPES_ME)
        if 'admin' in r['scopes']:
            r['scopes'].extend(constants.SCOPES_ADMIN)
        return UserAuthenticated(
            id=int(r['id']),
            token=token,
            scopes=r['scopes'],
        )
    return None


def cache_token(pipe: Pipeline, token: str, user_id: int, scopes: list[str]) -> None:  # type: ignore[type-arg]
    pipe.hset(f'seplis:tokens:{token}:user', 'id', str(user_id))
    pipe.hset(f'seplis:tokens:{token}:user', 'scopes', ' '.join(scopes))


async def rebuild_tokens() -> None:
    async with database.session() as session:
        result = await session.stream(
            sa.select(MToken).where(MToken.expires >= datetime.now(tz=UTC))
        )
        async for tokens in result.yield_per(10000):
            p = cast(Pipeline, database.redis.pipeline())
            for token in tokens:
                cache_token(
                    pipe=p,
                    token=token.token,
                    user_id=token.user_id,
                    scopes=token.scopes.split(' '),
                )
            await p.execute()
