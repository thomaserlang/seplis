import pickle
import hashlib
from seplis.decorators import new_session, auto_pipe
from seplis.api import models, constants
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from seplis.utils import random_key
from datetime import datetime, timedelta
from seplis.connections import database

class User(object):

    def to_dict(self, user_level=0):
        user = {
            'id': self.id,
            'name': self.name,
            'created': self.created,
            'level': self.level,
            'fan_of': self.fan_of,   
        }
        if user_level >= constants.LEVEL_SHOW_USER_EMAIL:
            user['email'] = self.email
        return user

    @classmethod
    def _format_from_query(cls, query):
        if not query: 
            return None
        user = cls()
        user.id = query.id
        user.name = query.name
        user.email = query.email
        user.created = query.created.isoformat()+'Z'
        user.level = query.level
        user.fan_of = query.fan_of
        return user

    @classmethod
    @auto_pipe
    def new(cls, name, email, password=None, level=0, pipe=None):
        '''
        :param name: str
        :param email: email
        :param password: str
            pbkdf2_sha256 encrypted!
        :param level: int
        :returns: `User()`
        '''
        with new_session() as session:
            user = models.User(
                name=name,
                email=email,
                password=password,
                created=datetime.utcnow(),
                level=level,
            )
            session.add(user)
            session.commit()
            user = cls._format_from_query(user)
            user.cache(pipe=pipe)
            user.cache_default_stat_fields(pipe=pipe)
            return user

    @auto_pipe
    def cache(self, pipe=None):
        pipe.sadd('users', self.id)
        for key, val in self.__dict__.items():
            pipe.hset(
                name='users:{}'.format(self.id),
                key=key,
                value=val,
            )

    @auto_pipe
    def cache_default_stat_fields(self, pipe=None):
        for key in constants.USER_STAT_FIELDS:
            pipe.hset(
                name='users:{}:stats'.format(self.id),
                key=key,
                value='0',
            )

    @classmethod
    def get_from_email(cls, email):
        '''
        
        :param email: str
        :returns: `User()`
        '''
        with new_session() as session:
            user = session.query(
                models.User,
            ).filter(
                models.User.email == email,
            ).first()
            return cls._format_from_query(user)

    @classmethod
    def _format_from_redis(cls, user):
        if not user:
            return
        u = User()
        u.__dict__.update(user)
        u.level = int(u.level)
        u.fan_of = int(u.fan_of)
        u.id = int(u.id)
        return u

    @classmethod
    def get(cls, id_):
        '''
        
        :param id_: str
        :returns: `User()`
        '''
        user = database.redis.hgetall('users:{}'.format(id_))
        if user:
            return cls._format_from_redis(user)
        with new_session() as session:
            user = session.query(
                models.User,
            ).filter(
                models.User.id == id_,
            ).first()
            user = cls._format_from_query(user)
            user.cache()
            return user

    @classmethod
    def login(cls, email, password):
        '''

        :param email: str
        :param password: str
        :returns: `User()`
        '''
        with new_session() as session:
            user = session.query(
                models.User,
            ).filter(
                models.User.email == email,
            ).first()
            if not user:
                return None
            if pbkdf2_sha256.verify(password, user.password):
                return cls._format_from_query(user)
        return None

    @classmethod
    def get_from_token(cls, token):
        user_token = database.redis.hgetall('tokens:{}'.format(token))
        if user_token:
            user = cls.get(user_token['user_id'])
            user.level = int(user_token['user_level'])
            return user

class Users(object):

    @classmethod
    def get(cls, ids):
        pipe = database.redis.pipeline()
        for id_ in ids:            
            pipe.hgetall('users:{}'.format(id_))
        users = [User._format_from_redis(user) for \
            user in pipe.execute()]
        return users

class Token(object):

    @classmethod
    def cache(cls, user_id, user_level, token, expire_days, pipe=None):
        _pipe = pipe if pipe else database.redis.pipeline()
        _pipe.hset('tokens:{}'.format(token), 'user_id', user_id)
        _pipe.hset('tokens:{}'.format(token), 'user_level', user_level)
        if expire_days:
            _pipe.expire('tokens:{}'.format(token), timedelta(days=expire_days))
        if not pipe:
            _pipe.execute()

    @classmethod
    def new(cls, user_id, user_level, app_id):
        '''

        :param user_id: int
        :param user_level: int
        :param app_id: int
        :returns: str
            access_token
        '''
        with new_session() as session:
            token = models.Token(
                user_id=user_id,
                user_level=user_level,
                app_id=app_id,
                token=random_key(),
                expires=datetime.utcnow() + timedelta(days=365),
            )
            session.add(token)
            session.commit()
            cls.cache(
                user_id=user_id,
                user_level=user_level,
                token=token.token,
                expire_days=365,
            )
            return token.token