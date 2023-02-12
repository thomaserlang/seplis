import sqlalchemy as sa
from starlette.concurrency import run_in_threadpool

from seplis.utils.sqlalchemy import UtcDateTime
from .. import schemas, exceptions
from .base import Base
from seplis import utils, logger
from seplis.api.database import database
from seplis.api import constants, exceptions, rebuild_cache
from datetime import datetime, timedelta, timezone
from passlib.hash import pbkdf2_sha256

class User_public(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(45), unique=True)
    created_at = sa.Column(UtcDateTime, default=datetime.utcnow)

class User(User_public):
    email = sa.Column(sa.String(100), unique=True)
    password = sa.Column(sa.String(200))
    level = sa.Column(sa.Integer, default=constants.LEVEL_USER)

    @classmethod
    async def save(cls, user_data: schemas.User_create | schemas.User_update, user_id: int = None) -> schemas.User:
        async with database.session() as session:
            data = user_data.dict(exclude_unset=True)
            if 'password' in data:
                data['password'] = await run_in_threadpool(pbkdf2_sha256.hash, user_data.password)

            if 'email' in data:
                e = await session.scalar(sa.select(User).where(
                    User.email == data['email'],
                    User.id != user_id,
                ))
                if e:
                    raise exceptions.User_email_duplicate()
            if 'username' in data:
                e = await session.scalar(sa.select(User).where(
                    User.username == data['username'],
                    User.id != user_id,
                ))
                if e:
                    raise exceptions.User_username_duplicate()
            if not user_id:
                r = await session.execute(sa.insert(User).values(data))
                user_id = r.lastrowid
            else:
                await session.execute(sa.update(User).where(User.id==user_id).values(data))
            user = await session.scalar(sa.select(User).where(User.id == user_id))
            await session.commit()
            return schemas.User.from_orm(user)


    @classmethod
    async def change_password(cls, user_id: int, new_password: str, current_token: str = None, expire_tokens = True):
        password = await run_in_threadpool(pbkdf2_sha256.hash, new_password)
        async with database.session() as session:
            await session.execute(sa.update(User).where(User.id == user_id).values(
                password=password,
            ))
            if expire_tokens:
                tokens = await session.scalars(sa.select(Token).where(
                    Token.user_id == user_id,
                    sa.or_(
                        Token.expires >= datetime.utcnow(),
                        Token.expires == None,
                    ),
                    Token.token != current_token,
                ))
                for token in tokens:
                    await session.delete(token)
                    await database.redis.delete(token.cache_name)

            await session.commit()


class Token(Base):
    __tablename__ = 'tokens'

    user_id = sa.Column(sa.Integer)
    app_id = sa.Column(sa.Integer)
    token = sa.Column(sa.String(255), primary_key=True)
    expires = sa.Column(UtcDateTime)
    user_level = sa.Column(sa.Integer)

    @staticmethod
    async def new_token(user_id: str, app_id: str | None = None, user_level: int = constants.LEVEL_USER, expires_days = constants.USER_TOKEN_EXPIRE_DAYS) -> str:
        async with database.session() as session:
            token = utils.random_key(255)
            await session.execute(sa.insert(Token).values(
                app_id=app_id,
                user_id=user_id,
                user_level=user_level,
                expires=datetime.now(tz=timezone.utc) + timedelta(days=expires_days),
                token=token,                                
            ))
            await session.commit()
            p = database.redis.pipeline()
            p.hset(f'seplis:tokens:{token}:user', 'id', user_id)
            p.hset(f'seplis:tokens:{token}:user', 'level', user_level)
            await p.execute()
            return token

    @classmethod
    async def get(cls, token: str) -> schemas.User_authenticated:
        r = await database.redis.hgetall(f'seplis:tokens:{token}:user')
        if r:
            d = schemas.User_authenticated.parse_obj(r)
            d.token = token
            return d


class User_series_settings(Base):
    __tablename__ = 'user_series_settings'
    
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    series_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    subtitle_lang = sa.Column(sa.String)
    audio_lang = sa.Column(sa.String)


@rebuild_cache.register('tokens')
def rebuild_tokens():
    with new_session() as session:
        for item in session.query(Token).filter(
                sa.or_(
                    Token.expires >= datetime.utcnow(),
                    Token.expires == None,
                )
            ).yield_per(10000):
            item.cache()
        session.commit()