from datetime import UTC, datetime
from typing import Any, cast

import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256  # ty: ignore[unresolved-import]
from starlette.concurrency import run_in_threadpool

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.database import database
from seplis.api.send_email import send_password_changed

from ..models.token_model import MToken
from ..models.user_model import MUser
from ..schemas.user_authentication_schemas import UserChangePassword
from ..schemas.user_schemas import User, UserCreate, UserPublic, UserUpdate


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


def user_public_mapper(user: MUser) -> UserPublic:
    return UserPublic(id=user.id, username=user.username)


async def get_users_by_username(
    username: str, session: AsyncSession | None = None
) -> list[UserPublic]:
    async with get_session(session) as session:
        users = await session.scalars(sa.select(MUser).where(MUser.username == username))
        return [user_public_mapper(user) for user in users]


async def prepare_user_data(data: dict[str, Any]) -> dict[str, Any]:
    prepared_data = data.copy()
    if 'password' in prepared_data:
        prepared_data['password'] = await run_in_threadpool(
            pbkdf2_sha256.hash, prepared_data['password']
        )

    if 'scopes' in prepared_data:
        prepared_data['scopes'] = ' '.join(prepared_data['scopes'])
    return prepared_data


async def ensure_unique_user_data(
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
            raise exceptions.UserEmailDuplicate()
    if 'username' in data and data['username'] is not None:
        e = await session.scalar(
            sa.select(MUser).where(
                MUser.username == data['username'],
                MUser.id != user_id,
            )
        )
        if e:
            raise exceptions.UserUsernameDuplicate()


async def create_user(
    data: UserCreate,
    session: AsyncSession | None = None,
) -> User:
    async with get_session(session) as session:
        prepared_data = await prepare_user_data(cast(dict[str, Any], data))
        await ensure_unique_user_data(prepared_data, session, user_id=None)

        r = cast(
            sa.Row[Any],
            await session.execute(sa.insert(MUser.__table__).values(prepared_data)),  # type: ignore
        )
        user_id = r.lastrowid
        user = await get_user(user_id=user_id, session=session)
        if not user:
            raise exceptions.UserUnknown()
        return user


async def update_user(
    user_id: int,
    data: UserUpdate,
    session: AsyncSession | None = None,
) -> User:
    async with get_session(session) as session:
        prepared_data = await prepare_user_data(cast(dict[str, Any], data))
        await ensure_unique_user_data(prepared_data, session, user_id=user_id)
        await session.execute(
            sa.update(MUser.__table__).where(MUser.id == user_id).values(prepared_data)  # type: ignore
        )
        user = await get_user(user_id=user_id, session=session)
        if not user:
            raise exceptions.UserUnknown()
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
            sa.update(MUser.__table__)  # type: ignore
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
                    sa.delete(MToken.__table__).where(MToken.token == token.token)  # type: ignore
                )
                await database.redis.delete(f'seplis:tokens:{token.token}:user')
        email = await session.scalar(sa.select(MUser.email).where(MUser.id == user_id))
        if email is not None:
            await send_password_changed(email)


async def change_own_password(
    user_id: int,
    data: UserChangePassword,
    current_token: str | None,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        password_hash = await session.scalar(
            sa.select(MUser.password).where(MUser.id == user_id)
        )
        if not password_hash:
            raise exceptions.UserUnknown()

        matches = await run_in_threadpool(
            pbkdf2_sha256.verify, data['current_password'], password_hash
        )
        if not matches:
            raise exceptions.WrongPassword()
        await change_password(
            user_id=user_id,
            new_password=data['new_password'],
            current_token=current_token,
        )
