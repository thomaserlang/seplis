import logging
import uuid
import sqlalchemy as sa
from .base import Base
from sqlalchemy import event, orm
from sqlalchemy.orm.attributes import get_history
from seplis import utils
from seplis.api.connections import database
from seplis.api import constants, exceptions, rebuild_cache
from seplis.api.decorators import new_session, auto_session
from seplis.api.base.pagination import Pagination
from datetime import datetime


class Play_server(Base):
    __tablename__ = 'play_servers'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, onupdate=datetime.utcnow)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    url = sa.Column(sa.String(200))
    external_id = sa.Column(sa.String(36))
    secret = sa.Column(sa.String(200))

    _cache_name_id = 'play_servers:{}'
    _cache_name_external_id = 'play_servers:external_id:{}'
    _cache_name_user_play_servers = 'users:{}:play_servers'

    def __init__(self, user_id, name, url, secret):
        self.user_id = user_id
        self.name = name
        self.url = url
        self.secret = secret
        self.external_id = str(uuid.uuid4())

    def serialize(self):
        return {
            'id': self.id,
            'created': utils.isoformat(self.created),
            'updated': utils.isoformat(self.updated) if self.updated else None,
            'user_id': self.user_id,
            'name': self.name,
            'url': self.url,
            'external_id': self.external_id,
            'secret': self.secret,
        }

    def after_insert(self):
        ps = Play_access(
            play_server_id=self.id,
            user_id=self.user_id,
        )
        self.session.add(ps)

    def after_upsert(self):
        self.cache()

    def after_delete(self):
        self.session.pipe.delete(self.cache_name_id)
        self.session.pipe.delete(Play_access._cache_name_access.format(
            self.id
        ))
        self.session.pipe.delete(self.cache_name_external_id)
        self.session.pipe.srem(self.cache_name_user_play_servers, self.id)

    def before_delete(self):
        '''Delete all access relations.'''
        access = self.session.query(Play_access).filter(
            Play_access.play_server_id == self.id,
        )
        for ps in access.yield_per(100):
            self.session.delete(ps)

    def cache(self):
        ps = self.serialize()
        name_id = self.cache_name_id
        for key in ps:
            self.session.pipe.hset(name_id, key, ps[key]) 
        self.session.pipe.set(self.cache_name_external_id, self.id)
        self.session.pipe.sadd(self.cache_name_user_play_servers, self.id)

    @property
    def cache_name_id(self):
        return self._cache_name_id.format(self.id)
    @property
    def cache_name_external_id(self):
        return self._cache_name_external_id.format(self.external_id)
    @property
    def cache_name_user_play_servers(self):
        return self._cache_name_user_play_servers.format(self.user_id)

    @classmethod
    def get(cls, id_):
        '''Returns one or more play servers if `id_` is a list.
        From cache.

        :param id_: int or list of int
        :returns: dict or list of dict
        '''
        if not isinstance(id_, list):
            ps = database.redis.hgetall(cls._cache_name_id.format(id_))
            if ps:
                utils.redis_sa_model_dict(ps, cls)
            return ps
        pipe = database.redis.pipeline()
        for i in id_:
            pipe.hgetall(cls._cache_name_id.format(i))
        pss = pipe.execute()
        result = []
        for ps in pss:
            if ps:
                result.append(ps)
                utils.redis_sa_model_dict(ps, cls)
        return result

    @classmethod
    def users_with_access(cls, id_, page=1, per_page=constants.PER_PAGE):
        '''Get a list of users with access to the play server.

        :param id_: int 
        :param page: int
        :param per_page: int
        :returns: `Pagination()`
        '''
        name = Play_access._cache_name_access.format(id_)
        pipe = database.redis.pipeline()
        pipe.sort(
            name=name,
            start=(int(page)-1)*per_page,
            num=per_page,
        )
        pipe.scard(name)
        user_ids, total = pipe.execute()
        from .user import User
        users = User.get(user_ids)
        return Pagination(
            page=page,
            per_page=per_page,
            total=total,
            records=users,
        )

    @classmethod
    def by_user_id(cls, user_id, access_to=False, page=1, per_page=constants.PER_PAGE):        
        '''Get a list of play servers owned by the user.
        Use `access_to` if you want play servers that the user has 
        access to.
        
        :param id_: int 
        :param access_to: bool
            False: Returns servers owned by the user.
            True: Returns servers that the user has access to.
        :param page: int
        :param per_page: int
        :returns: `Pagination()`
        '''
        pipe = database.redis.pipeline()
        name = cls._cache_name_user_play_servers.format(user_id) \
            if not access_to else \
                Play_access._cache_name_user_access_to.format(user_id)
        pipe.sort(
            name=name,
            start=(int(page)-1)*per_page,
            num=per_page,
        )
        pipe.scard(name)
        server_ids, total = pipe.execute()
        servers = cls.get(server_ids)
        return Pagination(
            page=page,
            per_page=per_page,
            total=total,
            records=servers,
        )

    @classmethod
    def has_access(cls, id_, user_id):
        '''Check if the user has access to the play server.

        :param id_: int
        :param user_id: int
        :returns: bool
        '''
        return database.redis.sismember(
            Play_access._cache_name_access.format(id_), 
            user_id
        )

    @classmethod
    @auto_session
    def give_access(cls, id_, user_id, session=None):
        '''Give a user access to a play server.
        This method can safely be called without checking if the
        user already has access.

        :param id_: int
        :param user_id: int
        '''
        if cls.has_access(id_, user_id):
            return
        ps = Play_access(
            play_server_id=id_,
            user_id=user_id,
        )
        session.add(ps)

    @classmethod
    @auto_session
    def remove_access(cls, id_, user_id, session=None):
        '''
        '''
        if not cls.has_access(id_, user_id):
            return
        ps = session.query(Play_access).filter(
            Play_access.play_server_id == id_,
            Play_access.user_id == user_id,
        ).first()
        if ps:
            session.delete(ps)

class Play_access(Base):
    __tablename__ = 'play_access'

    play_server_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, primary_key=True)

    _cache_name_access = 'play_servers:{}:access'
    _cache_name_user_access_to = 'users:{}:play_server_access'

    def after_insert(self):
        self.cache()

    def after_delete(self):
        self.session.pipe.srem(self.cache_name_access, self.user_id)
        self.session.pipe.srem(self.cache_name_user_access_to, self.play_server_id)

    def cache(self):
        self.session.pipe.sadd(self.cache_name_access, self.user_id)
        self.session.pipe.sadd(self.cache_name_user_access_to, self.play_server_id)

    @property
    def cache_name_access(self):
        return self._cache_name_access.format(self.play_server_id)
    @property
    def cache_name_user_access_to(self):
        return self._cache_name_user_access_to.format(self.user_id)

@rebuild_cache.register('play_servers')
def rebuild_play_servers():
    with new_session() as session:
        for item in session.query(Play_server).yield_per(10000):
            item.cache()
        for item in session.query(Play_access).yield_per(10000):
            item.cache()
        session.commit()