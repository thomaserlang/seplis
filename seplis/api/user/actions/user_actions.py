from datetime import UTC, datetime
from typing import Any, cast

import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256
from starlette.concurrency import run_in_threadpool

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.database import database
from seplis.api.send_email import send_password_changed

from ..models.token_model import MToken
from ..models.user_model import MUser
from ..schemas.user_schemas import User, UserCreate, UserUpdate


async def get_user(user_id: int, session: AsyncSession | None = None) -> User | None:
    async with get_session(session) as session:
        user = await session.scalar(sa.select(MUser).where(MUser.id == user_id))
        if not user:
            return None
        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            scopes=user.scopes.split(' ')
            if isinstance(user.scopes, str)
            else user.scopes,
        )


async def _prepare_user_data(data: dict[str, Any]) -> dict[str, Any]:
    _data = data.copy()
    if 'password' in _data:
        _data['password'] = await run_in_threadpool(pbkdf2_sha256.hash, _data['password'])

    if 'scopes' in _data:
        _data['scopes'] = ' '.join(_data['scopes'])
    return _data


async def _ensure_unique_user_data(
    data: dict[str, Any], session: AsyncSession, user_id: int | None
) -> None:
    if 'email' in data and data['email'] is not None:
        e = await session.scalar(
            sa.select(MUser).where(
                MUser.email == data['email'],
                MUser.id != user_id,
            )
        )
        if e:
            raise exceptions.User_email_duplicate()
    if 'username' in data and data['username'] is not None:
        e = await session.scalar(
            sa.select(MUser).where(
                MUser.username == data['username'],
                MUser.id != user_id,
            )
        )
        if e:
            raise exceptions.User_username_duplicate()


async def create_user(
    data: UserCreate,
    session: AsyncSession | None = None,
) -> User:
    async with get_session(session) as session:
        _data = await _prepare_user_data(cast(dict[str, Any], data))
        await _ensure_unique_user_data(_data, session, user_id=None)

        r = cast(sa.Row[Any], await session.execute(sa.insert(MUser).values(_data)))
        user_id = r.lastrowid
        user = await get_user(user_id=user_id, session=session)
        if not user:
            raise exceptions.User_unknown()
        return user


async def update_user(
    user_id: int,
    data: UserUpdate,
    session: AsyncSession | None = None,
) -> User:
    async with get_session(session) as session:
        _data = await _prepare_user_data(cast(dict[str, Any], data))
        await _ensure_unique_user_data(_data, session, user_id=user_id)
        await session.execute(sa.update(MUser).where(MUser.id == user_id).values(_data))
        user = await get_user(user_id=user_id, session=session)
        if not user:
            raise exceptions.User_unknown()
        return user


async def change_password(
    user_id: int,
    new_password: str,
    session: AsyncSession | None = None,
    current_token: str | None = None,
    expire_tokens: bool = True,
) -> None:
    async with get_session(session) as session:
        password = await run_in_threadpool(pbkdf2_sha256.hash, new_password)
        await session.execute(
            sa.update(MUser)
            .where(MUser.id == user_id)
            .values(
                password=password,
            )
        )
        if expire_tokens:
            tokens = await session.scalars(
                sa.select(MToken).where(
                    MToken.user_id == user_id,
                    sa.or_(
                        MToken.expires >= datetime.now(tz=UTC),
                        MToken.expires.is_(None),
                    ),
                    MToken.token != current_token,
                )
            )
            for token in tokens:
                await session.execute(
                    sa.delete(MToken).where(MToken.token == token.token)
                )
                await database.redis.delete(f'seplis:tokens:{token.token}:user')
        email = await session.scalar(sa.select(MUser.email).where(MUser.id == user_id))
        if email is not None:
            await send_password_changed(email)
