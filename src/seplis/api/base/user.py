import pickle
import hashlib
from seplis.decorators import new_session
from seplis.api import models
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from seplis.utils import random_key
from datetime import datetime, timedelta
from seplis.connections import database

class User(object):

    def to_dict(self):
        return self.__dict__

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
        user.follows = 0
        return user

    @classmethod
    def new(cls, name, email, password=None, level=0):
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
            user.cache()
            return user

    def cache(self, pipe=None):
        _pipe = pipe if pipe else database.redis.pipeline()
        _pipe.sadd('users', self.id)
        for key, val in self.__dict__.items():
            _pipe.hset(
                name='users:{}'.format(self.id),
                key=key,
                value=val,
            )
        if not pipe:
            _pipe.execute()

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
    def get(cls, id_):
        '''
        
        :param id_: str
        :returns: `User()`
        '''
        user = database.redis.hgetall('users:{}'.format(id_))
        if user:
            u = User()
            u.__dict__.update(user)
            u.level = int(u.level)
            u.follows = int(u.follows)
            u.id = int(u.id)
            return u
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