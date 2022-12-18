import logging
import sqlalchemy as sa
from .base import Base
from sqlalchemy import orm
from sqlalchemy.orm.attributes import get_history
from seplis import utils
from seplis.api.connections import database
from seplis.api import rebuild_cache
from datetime import datetime

class App(Base):
    __tablename__ = 'apps'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    client_id = sa.Column(sa.String(45))
    client_secret = sa.Column(sa.String(45))
    redirect_uri = sa.Column(sa.String(45))
    level = sa.Column(sa.Integer)
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, onupdate=datetime.utcnow)

    _cache_name_id = 'apps:{}'
    _cache_name_client_id = 'apps:client_id:{}'

    def __init__(self, user_id, name, level, redirect_uri=None):
        '''
        :param user_id: int
        :param name: str
        :param level: int
        :param redirect_uri: str
        '''
        self.user_id = user_id
        self.name = name
        self.level = level
        self.redirect_uri = redirect_uri
        self.client_id = utils.random_key()
        self.client_secret = utils.random_key()
        self.created = datetime.utcnow()

    @classmethod
    def get(cls, id_):
        '''Returns one or more apps from the cache if `id_` is a list.

        :param id_: int or list of int
        :returns: dict or list of dict
        '''
        if not isinstance(id_, list):
            app = database.redis.hgetall(cls._cache_name_id.format(id_))
            if app:
                utils.redis_sa_model_dict(app, App)
            return app
        pipe = database.redis.pipeline()
        for i in id_:
            pipe.hgetall(cls._cache_name_id.format(id_))
        apps = pipe.execute()
        result = []
        for app in apps:
            if app:
                result.append(app)
                utils.redis_sa_model_dict(app, App)
        return result

    @classmethod
    def by_client_id(cls, client_id):
        '''Returns an app from the cache by it's client_id.

        :param client_id: str
        :returns: dict
        '''
        app_id = database.redis.get(cls._cache_name_client_id.format(client_id))
        if not app_id:
            return
        return cls.get(int(app_id))

    def cache(self):
        session = orm.Session.object_session(self)
        app = self.serialize()
        name = self.cache_name_id
        for key in app:
            session.pipe.hset(name, key, app[key] if app[key] != None else 'None')
        session.pipe.set(self.cache_name_client_id, self.id)

    @property
    def cache_name_id(self):
        return self._cache_name_id.format(self.id)
    @property
    def cache_name_client_id(self):
        return self._cache_name_client_id.format(self.client_id)

@rebuild_cache.register('apps')
def rebuild_apps():
    with new_session() as session:
        for item in session.query(App).yield_per(10000):
            item.cache()
        session.commit()