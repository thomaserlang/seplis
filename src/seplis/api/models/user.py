import logging
import sqlalchemy as sa
import hashlib
from .base import Base
from sqlalchemy import event, orm
from sqlalchemy.orm.attributes import get_history
from seplis import utils
from seplis.api.connections import database
from seplis.api import constants, exceptions, rebuild_cache
from seplis.api.decorators import new_session, auto_session
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256

class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(45), unique=True)
    email = sa.Column(sa.String(100), unique=True)
    password = sa.Column(sa.CHAR(87))
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    level = sa.Column(sa.Integer, default=constants.LEVEL_USER)

    fan_of = sa.Column(sa.Integer, default=0)
    watched = sa.Column(sa.Integer, default=0)

    _cache_name_id = 'users:{}'
    _cache_name_id_password = 'users:{}:password'
    _cache_name_email = 'users:email:{}'
    _cache_name_name = 'users:name:{}'
    _cache_name_stats = 'users:{}:stats'

    _user_stat_fields = (
        'fan_of',
        'episodes_watched',
    )

    def serialize(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'level': self.level,
            'created_at': utils.isoformat(self.created_at),
        }
        return data

    @classmethod
    def get(cls, id_):
        '''Returns one or more users from the cache if `id_` is a list.

        :param id_: int or list of int
        :param with_email: bool
        :returns: dict or list of dict
        '''
        if not isinstance(id_, list):
            user = database.redis.hgetall(cls._cache_name_id.format(id_))
            if user:
                utils.redis_sa_model_dict(user, User)                
            return user
        pipe = database.redis.pipeline()
        for i in id_:
            pipe.hgetall(cls._cache_name_id.format(i))
        users = pipe.execute()
        result = []
        for user in users:
            if user:
                result.append(user)
                utils.redis_sa_model_dict(user, User)
        return users

    @classmethod
    def by_email_or_username(cls, email_or_username):
        '''Returns a user from cache by it's email or username.

        :param email_or_username: str
        :returns: dict
        '''
        if isinstance(email_or_username, str):
            lookup = hashlib.md5(email_or_username.lower().encode('utf-8')).hexdigest()
            user_id = database.redis.get(cls._cache_name_email.format(lookup))
            if not user_id:
                user_id = database.redis.get(cls._cache_name_name.format(
                    lookup
                ))
            if not user_id:
                return
        elif isinstance(email_or_username, int):
            user_id = email_or_username
        else:
            raise Exception('Unknown type')
        return cls.get(user_id)

    @classmethod
    def by_token(cls, token):
        '''Returns a user from cache by it's login token.

        :param token: str
        :returns: dict
        '''
        user_token = database.redis.hgetall('tokens:{}'.format(token))
        if user_token:
            user = cls.get(user_token['user_id'])
            user['level'] = int(user_token['user_level'])
            return user

    @classmethod
    def login(cls, email_or_username, password):
        '''Tries to log the user in by it's email or username.
        Returns the user as a dict if successful otherwise returns `None`.

        :param email_or_username: str
        :param password: str
        :returns: dict
        '''
        user = cls.by_email_or_username(email_or_username)
        if not user:
            return
        user_password = database.redis.get(cls._cache_name_id_password.format(
            user['id']
        ))
        if user_password.startswith('$pbkdf2-sha256$'):
            if pbkdf2_sha256.verify(password, user_password):
                return user
        elif user_password.startswith('seplis_old'):
            if seplis_v2_password_validate(password, user_password):
                cls.change_password(user['id'], password)
                return user

    @classmethod
    @auto_session
    def change_password(cls, user_id, new_password, session=None):
        '''

        :param user_id: int
        :param new_password: str
            Must be a plain text password. This method will 
            encrypt it before updating.
        :raises: `exceptions.User_unknown()`
            Raised if the user was not found.
        '''
        user = session.query(
            cls,
        ).filter(
            cls.id == user_id,
        ).first()
        if not user:
            raise exceptions.User_unknown()
        user.password = pbkdf2_sha256.hash(new_password)

    def after_insert(self):
        self.cache_user_default_stats()

    def after_upsert(self):
        self.cache()

    def after_delete(self):
        self.session.pipe.delete(self.cache_name_id)
        self.session.pipe.delete(self.cache_name_name)
        self.session.pipe.delete(self.cache_name_email)
        self.session.pipe.delete(self.cache_name_stats)
        self.session.pipe.delete(self.cache_name_id_password)

    def cache(self):
        '''Caches users meta info without stats. See `cache_user_default_stats`
        for the stats.
        This method is called automatically after update or insert. 
        '''
        name_user = self.cache_name_id
        user = self.serialize()
        for key in user:
            self.session.pipe.hset(name_user, key, user[key] if user[key] != None else 'None')
        self.session.pipe.set(self.cache_name_email, self.id)
        self.session.pipe.set(self.cache_name_name, self.id)
        self.session.pipe.set(self.cache_name_id_password, self.password or '')  

    def cache_user_default_stats(self):
        '''Defaults the user's stats field to 0.
        Each model that uses any of the stat fields is responsible
        for incrementing and restoring the values after a cache
        rebuild.
        This method is automatically called on update, insert and 
        on a cache rebuild.
        '''
        name = self.cache_name_stats
        for f in self._user_stat_fields:
            self.session.pipe.hsetnx(self.cache_name_stats, f, '0')

    @property
    def cache_name_id(self):
        return self._cache_name_id.format(self.id)
    @property
    def cache_name_id_password(self):
        return self._cache_name_id_password.format(self.id)
    @property
    def cache_name_email(self):
        return self._cache_name_email.format(
            hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        )
    @property
    def cache_name_name(self):
        return self._cache_name_name.format(
            hashlib.md5(self.name.lower().encode('utf-8')).hexdigest(),
        )
    @property
    def cache_name_stats(self):
        return self._cache_name_stats.format(self.id)

def seplis_v2_password_validate(password, password_hash):
    import hashlib
    s = password_hash.split(':')
    if len(s) != 3:
        raise Exception('invalid seplis v2 password')
    if s[0] != 'seplis_old':
        raise Exception('invalid seplis v2 password')
    pw = password+s[1]
    for i in range(1, 10790):
        pw = hashlib.sha512(pw.encode('utf-8')).hexdigest()
    return pw == s[2]

class Token(Base):
    __tablename__ = 'tokens'

    user_id = sa.Column(sa.Integer)
    app_id = sa.Column(sa.Integer)
    token = sa.Column(sa.String(45), primary_key=True)
    expires = sa.Column(sa.DateTime)
    user_level = sa.Column(sa.Integer)

    _cache_name  = 'tokens:{}'

    def __init__(self, app_id, user_id, user_level, expires=None):
        '''Auto genrates a token and sets expires to a year from now
        if it's `None`.

        :param app_id: int
        :param user_id: int
        :param user_level: int
        :param expires: datetime
        '''
        self.app_id = app_id
        self.user_id = user_id
        self.user_level = user_level
        self.expires = expires if expires else \
            datetime.utcnow() + timedelta(days=constants.USER_TOKEN_EXPIRE_DAYS)
        self.token = utils.random_key()

    def after_insert(self):
        self.cache()

    def after_delete(self):        
        self.session.pipe.delete(self.cache_name)

    def cache(self):
        name = self.cache_name
        self.session.pipe.hset(name, 'user_id', self.user_id)
        self.session.pipe.hset(name, 'user_level', self.user_level)
        if self.expires:
            self.session.pipe.expireat(name, self.expires)

    @property
    def cache_name(self):
        return self._cache_name.format(self.token)

class User_show_subtitle_lang(Base):
    __tablename__ = 'user_show_subtitle_lang'
    
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    subtitle_lang = sa.Column(sa.String)
    audio_lang = sa.Column(sa.String)

    _cache_name = 'users:{}:subtitle_lang:shows:{}'

    def serialize(self):
        return {
            'subtitle_lag': self.subtitle_lang,
            'audio_lang': self.audio_lang,
        }

    def after_upsert(self):
        self.cache()

    def after_delete(self):
        self.session.pipe.delete(self.cache_name)

    @classmethod
    def get(cls, user_id, show_id):
        '''Retrive a users's default subtitle settings for a show from the cache.
        :param user_id: int
        :param show_id: int
        :return: dict
            {
                "subtitle_lang": "en",
                "audio_lang": "jpn"
            }
        '''
        data = database.redis.hgetall(cls.gen_cache_name(
            user_id=user_id,
            show_id=show_id,
        ))
        if data:
            return utils.redis_sa_model_dict(data, cls)

    @classmethod
    def gen_cache_name(cls, user_id, show_id):
        return cls._cache_name.format(user_id, show_id)
    @property
    def cache_name(self):
        return self.gen_cache_name(
            user_id=self.user_id, 
            show_id=self.show_id
        )

    def cache(self):
        name = self.cache_name
        self.session.pipe.hset(name, 'subtitle_lang', self.subtitle_lang if self.subtitle_lang != None else 'None' )
        self.session.pipe.hset(name, 'audio_lang', self.audio_lang if self.audio_lang != None else 'None')

@rebuild_cache.register('users')
def rebuild_users():
    with new_session() as session:
        for item in session.query(User).yield_per(10000):
            item.cache()
            item.cache_user_default_stats()
        session.commit()

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

@rebuild_cache.register('user_show_subtitle_lang')
def rebuild_user_show_subtitle_lang():
    with new_session() as session:
        for item in session.query(User_show_subtitle_lang).yield_per(10000):
            item.cache()
        session.commit()