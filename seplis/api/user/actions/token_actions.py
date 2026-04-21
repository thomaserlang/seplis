from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from redis.asyncio.client import Pipeline

from seplis import utils
from seplis.api import constants
from seplis.api.database import database

from ..models.token_model import MToken
from ..schemas.user_authentication_schemas import UserAuthenticated


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
            sa.insert(MToken).values(
                app_id=app_id,
                user_id=user_id,
                expires=datetime.now(tz=UTC) + timedelta(days=expires_days),
                token=token,
                scopes=' '.join(scopes),
            )
        )
        await session.commit()
        p: Pipeline = database.redis.pipeline()  # type: ignore[assignment]
        cache_token(p, token, user_id, scopes)
        await p.execute()
        return token


async def get_authenticated_user(token: str) -> UserAuthenticated | None:
    r = await database.redis.hgetall(f'seplis:tokens:{token}:user')  # type: ignore[assignment]
    if r:
        r['scopes'] = r['scopes'].split(' ') if r.get('scopes') else ['me']
        if 'me' in r['scopes']:
            r['scopes'].extend(constants.SCOPES_ME)
        if 'admin' in r['scopes']:
            r['scopes'].extend(constants.SCOPES_ADMIN)
        d = UserAuthenticated.model_validate(r)
        d.token = token
        return d
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
            p: Pipeline = database.redis.pipeline()  # type: ignore[assignment]
            for token in tokens:
                cache_token(
                    pipe=p,
                    token=token.token,
                    user_id=token.user_id,
                    scopes=token.scopes.split(' '),
                )
            await p.execute()
