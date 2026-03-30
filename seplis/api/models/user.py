from datetime import UTC, datetime, timedelta
from typing import Any, cast

import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256
from redis.asyncio.client import Pipeline
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from starlette.concurrency import run_in_threadpool

from seplis import utils
from seplis.api import constants, exceptions
from seplis.api.database import auto_session, database
from seplis.api.send_email import send_password_changed
from seplis.utils.sqlalchemy import UtcDateTime

from .. import schemas
from .base import Base


class User_public(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(45), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime, server_default=sa.func.now()
    )


class User(User_public):
    email: Mapped[str] = mapped_column(sa.String(100), unique=True)
    password: Mapped[str] = mapped_column(sa.String(200))
    scopes: Mapped[str] = mapped_column(sa.String(2000), server_default='me')

    @classmethod
    async def save(
        cls, data: schemas.User_create | schemas.User_update, user_id: int | None = None
    ) -> schemas.User:
        async with database.session() as session:
            _data = data.model_dump(exclude_unset=True)
            if 'password' in _data:
                _data['password'] = await run_in_threadpool(
                    pbkdf2_sha256.hash, _data['password']
                )

            if 'scopes' in _data:
                _data['scopes'] = ' '.join(_data['scopes'])

            if 'email' in _data:
                e = await session.scalar(
                    sa.select(User).where(
                        User.email == _data['email'],
                        User.id != user_id,
                    )
                )
                if e:
                    raise exceptions.User_email_duplicate()
            if 'username' in _data:
                e = await session.scalar(
                    sa.select(User).where(
                        User.username == _data['username'],
                        User.id != user_id,
                    )
                )
                if e:
                    raise exceptions.User_username_duplicate()
            if not user_id:
                r = cast(
                    sa.Row[Any], await session.execute(sa.insert(User).values(_data))
                )
                user_id = r.lastrowid
            else:
                await session.execute(
                    sa.update(User).where(User.id == user_id).values(_data)
                )
            user = await session.scalar(sa.select(User).where(User.id == user_id))
            await session.commit()
            return schemas.User.model_validate(user)

    @classmethod
    @auto_session
    async def change_password(
        cls,
        user_id: int,
        new_password: str,
        session: AsyncSession,
        current_token: str | None = None,
        expire_tokens: bool = True,
    ) -> None:
        password = await run_in_threadpool(pbkdf2_sha256.hash, new_password)
        await session.execute(
            sa.update(User)
            .where(User.id == user_id)
            .values(
                password=password,
            )
        )
        if expire_tokens:
            tokens = await session.scalars(
                sa.select(Token).where(
                    Token.user_id == user_id,
                    sa.or_(
                        Token.expires >= datetime.now(tz=UTC),
                        Token.expires.is_(None),
                    ),
                    Token.token != current_token,
                )
            )
            for token in tokens:
                await session.execute(sa.delete(Token).where(Token.token == token.token))
                await database.redis.delete(f'seplis:tokens:{token.token}:user')
        email = await session.scalar(sa.select(User.email).where(User.id == user_id))
        if email is not None:
            await send_password_changed(email)


class Token(Base):
    __tablename__ = 'tokens'

    user_id: Mapped[int | None] = mapped_column(sa.Integer)
    app_id: Mapped[int | None] = mapped_column(sa.Integer)
    token: Mapped[str] = mapped_column(sa.String(2000), primary_key=True)
    expires: Mapped[datetime | None] = mapped_column(UtcDateTime)
    scopes: Mapped[str] = mapped_column(sa.String(2000), server_default='me')

    @staticmethod
    async def new_token(
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
                sa.insert(Token).values(
                    app_id=app_id,
                    user_id=user_id,
                    expires=datetime.now(tz=UTC) + timedelta(days=expires_days),
                    token=token,
                    scopes=' '.join(scopes),
                )
            )
            await session.commit()
            p: Pipeline = database.redis.pipeline()  # type: ignore[assignment]
            Token.cache(p, token, user_id, scopes)
            await p.execute()
            return token

    @staticmethod
    def cache(pipe: Pipeline, token: str, user_id: int, scopes: list[str]) -> None:  # type: ignore[type-arg]
        pipe.hset(f'seplis:tokens:{token}:user', 'id', str(user_id))
        pipe.hset(f'seplis:tokens:{token}:user', 'scopes', ' '.join(scopes))

    @classmethod
    async def get(cls, token: str) -> schemas.User_authenticated | None:
        r = await database.redis.hgetall(f'seplis:tokens:{token}:user')  # type: ignore[assignment]
        if r:
            r['scopes'] = r['scopes'].split(' ') if r.get('scopes') else ['me']
            if 'me' in r['scopes']:
                r['scopes'].extend(constants.SCOPES_ME)
            if 'admin' in r['scopes']:
                r['scopes'].extend(constants.SCOPES_ADMIN)
            d = schemas.User_authenticated.model_validate(r)
            d.token = token
            return d
        return None


class User_series_settings(Base):
    __tablename__ = 'user_series_settings'

    user_id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=False
    )
    series_id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=False
    )
    subtitle_lang: Mapped[str | None] = mapped_column(sa.String)
    audio_lang: Mapped[str | None] = mapped_column(sa.String)


async def rebuild_tokens() -> None:
    async with database.session() as session:
        result = await session.stream(
            sa.select(Token).where(Token.expires >= datetime.now(tz=UTC))
        )
        async for tokens in result.yield_per(10000):
            p: Pipeline = database.redis.pipeline()  # type: ignore[assignment]
            for token in tokens:
                Token.cache(
                    pipe=p,
                    token=token.token,
                    user_id=token.user_id,
                    scopes=token.scopes.split(' '),
                )
            await p.execute()
