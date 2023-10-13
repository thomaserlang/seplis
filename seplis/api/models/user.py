import sqlalchemy as sa
from starlette.concurrency import run_in_threadpool
from seplis.api.send_email import send_password_changed
from seplis.utils.sqlalchemy import UtcDateTime
from .. import schemas, exceptions
from .base import Base
from seplis import utils
from seplis.api.database import auto_session, database
from seplis.api import constants, exceptions
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
    scopes = sa.Column(sa.String(2000), server_default='me')

    @classmethod
    async def save(cls, data: schemas.User_create | schemas.User_update, user_id: int = None) -> schemas.User:
        async with database.session() as session:
            _data = data.model_dump(exclude_unset=True)
            if 'password' in _data:
                _data['password'] = await run_in_threadpool(pbkdf2_sha256.hash, data.password)

            if 'scopes' in _data:
                _data['scopes'] = ' '.join(_data['scopes'])

            if 'email' in _data:
                e = await session.scalar(sa.select(User).where(
                    User.email == _data['email'],
                    User.id != user_id,
                ))
                if e:
                    raise exceptions.User_email_duplicate()
            if 'username' in _data:
                e = await session.scalar(sa.select(User).where(
                    User.username == _data['username'],
                    User.id != user_id,
                ))
                if e:
                    raise exceptions.User_username_duplicate()
            if not user_id:
                r = await session.execute(sa.insert(User).values(_data))
                user_id = r.lastrowid
            else:
                await session.execute(sa.update(User).where(User.id==user_id).values(_data))
            user = await session.scalar(sa.select(User).where(User.id == user_id))
            await session.commit()
            return schemas.User.model_validate(user)


    @classmethod
    @auto_session
    async def change_password(cls, user_id: int, new_password: str, current_token: str = None, expire_tokens = True, session=None):
        password = await run_in_threadpool(pbkdf2_sha256.hash, new_password)
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
                await session.execute(sa.delete(Token).where(Token.token == token.token))
                await database.redis.delete(f'seplis:tokens:{token.token}:user')
        email = await session.scalar(sa.select(User.email).where(User.id == user_id))
        await send_password_changed(email)


class Token(Base):
    __tablename__ = 'tokens'

    user_id = sa.Column(sa.Integer)
    app_id = sa.Column(sa.Integer)
    token = sa.Column(sa.String(2000), primary_key=True)
    expires = sa.Column(UtcDateTime)
    scopes = sa.Column(sa.String(2000), server_default='me')

    @staticmethod
    async def new_token(
        user_id: str, 
        scopes: list[str] | str,
        app_id: str | None = None, 
        expires_days = constants.USER_TOKEN_EXPIRE_DAYS
    ) -> str:
        if isinstance(scopes, str):
            scopes = scopes.split(' ')
        async with database.session() as session:
            token = utils.random_key(256)
            await session.execute(sa.insert(Token).values(
                app_id=app_id,
                user_id=user_id,
                expires=datetime.now(tz=timezone.utc) + timedelta(days=expires_days),
                token=token,
                scopes=' '.join(scopes),
            ))
            await session.commit()
            p = database.redis.pipeline()
            Token.cache(p, token, user_id, scopes)
            await p.execute()
            return token
    
    @staticmethod
    def cache(pipe, token: str, user_id: str, scopes: list[str]):
        pipe.hset(f'seplis:tokens:{token}:user', 'id', user_id)
        pipe.hset(f'seplis:tokens:{token}:user', 'scopes', ' '.join(scopes))

    @classmethod
    async def get(cls, token: str) -> schemas.User_authenticated | None:
        r = await database.redis.hgetall(f'seplis:tokens:{token}:user')
        if r:
            r['scopes'] = r['scopes'].split(' ') if r.get('scopes') else ['me']
            if 'me' in r['scopes']:
                r['scopes'].extend(constants.SCOPES_ME)
            d = schemas.User_authenticated.model_validate(r)
            d.token = token
            return d


class User_series_settings(Base):
    __tablename__ = 'user_series_settings'
    
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    series_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    subtitle_lang = sa.Column(sa.String)
    audio_lang = sa.Column(sa.String)


async def rebuild_tokens():
    async with database.session() as session:
        result = await session.stream(sa.select(Token).where(Token.expires >= datetime.now(tz=timezone.utc)))
        async for tokens in result.yield_per(10000):
            p = database.redis.pipeline()
            for token in tokens:
                Token.cache(
                    pipe=p, 
                    token=token.token, 
                    user_id=token.user_id,
                    scopes=token.scopes.split(' '),
                )
            await p.execute()