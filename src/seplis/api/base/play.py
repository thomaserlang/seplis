import uuid
from seplis.api import models, constants
from seplis.api.decorators import auto_session, auto_pipe
from seplis.api.connections import database
from seplis.api.base.pagination import Pagination
from seplis.api.base.user import Users
from datetime import datetime

class Play_server(object):

    def __init__(self, id, created, updated, user_id, name,
        address, external_id, secret):
        '''

        :param id: int
        :param created: datetime
        :param updated: datetime
        :param user_id: int
        :param name: str
        :param address: str
        :param external_id: str
        :param secret: str
        '''
        self.id = id
        self.created = created
        self.updated = updated
        self.user_id = user_id
        self.name = name
        self.address = address
        self.external_id = external_id
        self.secret = secret

    def to_dict(self):
        return self.__dict__

    @classmethod
    def _format_from_row(cls, row):
        if not row:
            return
        return cls(
            id=row.id,
            created=row.created,
            updated=row.updated,
            user_id=row.user_id,
            name=row.name,
            address=row.address,
            external_id=row.external_id,
            secret=row.secret,
        )

    @classmethod
    @auto_session
    @auto_pipe
    def new(cls, user_id, name, address, secret, 
        session=None, pipe=None):
        server = models.Play_server(
            user_id=int(user_id),
            name=name,
            address=address,
            created=datetime.utcnow(),
            external_id=str(uuid.uuid4()),
            secret=secret,
        )
        session.add(server)
        session.flush()
        server = cls._format_from_row(server)
        server.cache(pipe=pipe)
        Play_user_access.add(
            play_server_id=server.id,
            user_id=user_id,
            pipe=pipe,
        )
        return server

    @auto_session
    @auto_pipe
    def save(self, session=None, pipe=None):
        self.updated = datetime.utcnow()
        session.query(
            models.Play_server.id == self.id,
        ).update({
            'updated': self.updated,
            'user_id': self.user_id,
            'name': self.name,
            'address': self.address,
            'secret': self.secret,
        })
        self.cache(pipe=pipe)

    @auto_session
    @auto_pipe
    def delete(self, session=None, pipe=None):
        deleted = session.query(models.Play_server).filter(
            models.Play_server.id == self.id,
        ).delete()
        if not deleted:
            return False
        pipe.delete('play_servers:{}'.format(self.id))
        return True

    @classmethod
    def _format_from_redis(cls, server):
        if not server:
            return
        ps = Play_server(
            id=int(server['id']),
            created=server['created'],
            updated=server['updated'] if server['updated'] != 'None' else None,
            user_id=int(server['user_id']),
            name=server['name'],
            address=server['address'],
            external_id=server['external_id'],
            secret=server['secret'],
        )
        return ps

    @classmethod
    def get(cls, id_):
        server = database.redis.hgetall('play_servers:{}'.format(id_))
        return cls._format_from_redis(server)

    @auto_pipe
    def cache(self, pipe=None):
        for key, val in self.__dict__.items():
            pipe.hset(
                name='play_servers:{}'.format(self.id),
                key=key,
                value=val,
            )
        pipe.set(
            'play_servers:external_id:{}'.format(self.external_id),
            self.id,
        )
        pipe.sadd(
            'users:{}:play_servers'.format(self.user_id),
            self.id,
        )

    @classmethod
    def get_users(self, id_, page=1, per_page=constants.PER_PAGE):
        name = 'play_server_user_access:{}'.format(id_)

        pipe = database.redis.pipeline()
        pipe.sort(
            name=name,
            start=(int(page)-1)*per_page,
            num=per_page,
        )
        pipe.scard(name)
        user_ids, total = pipe.execute()
        users = Users.get(user_ids)
        return Pagination(
            page=page,
            per_page=per_page,
            total=total,
            records=users,
        )

class Play_servers(object):

    @classmethod
    def get_by_user_id(cls, user_id, page=1, per_page=constants.PER_PAGE):
        '''

        :param user_id: int
        :param page: int
        :params per_page: int
        :returns: `Pagination()`
        '''
        pipe = database.redis.pipeline()
        name = 'users:{}:play_servers'.format(user_id)
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
    def get(cls, ids):
        pipe = database.redis.pipeline()
        for id_ in ids:
            pipe.hgetall('play_servers:{}'.format(id_))
        return [Play_server._format_from_redis(server) \
            for server in pipe.execute()]

class Play_user_access(object):

    @classmethod
    @auto_session
    @auto_pipe
    def add(cls, play_server_id, user_id, session=None, pipe=None):
        '''

        :param play_server_id: int
        :param user_id: int
        '''
        pa = models.Play_access(
            play_server_id=play_server_id,
            user_id=user_id,
        )
        session.merge(pa)
        cls.cache(
            play_server_id=play_server_id,
            user_id=user_id,
            pipe=pipe,
        )

    @classmethod
    @auto_pipe
    def cache(cls, play_server_id, user_id, pipe):
        '''

        :param play_server_id: int
        :param user_id: int
        '''
        pipe.sadd(
            'play_server_user_access:{}'.format(play_server_id), 
            user_id
        )
        pipe.sadd(
            'users:{}:play_server_access'.format(user_id),
            play_server_id,
        )

    @classmethod
    @auto_session
    @auto_pipe
    def delete(cls, play_server_id, user_id, session=None, pipe=None):
        '''

        :param play_server_id: int
        :param user_id: int
        :returns: bool
        '''
        deleted = session.query(
            models.Play_access,
        ).filter(
            models.Play_access.play_server_id == play_server_id,
            models.Play_access.user_id == user_id,
        ).delete()
        if not deleted:
            return False
        pipe.srem(
            'play_server_user_access:{}'.format(play_server_id), 
            user_id
        )
        pipe.srem(
            'users:{}:play_server_access'.format(user_id),
            play_server_id,
        )
        return True

    @classmethod
    def get_servers(cls, user_id, page=1, per_page=constants.PER_PAGE):
        '''

        :param user_id: int
        :returns: `Pagination()`
        '''
        name = 'users:{}:play_server_access'.format(user_id)
        pipe = database.redis.pipeline()
        pipe.sort(
            name=name,
            start=(int(page)-1)*per_page,
            num=per_page,
        )
        pipe.scard(name)
        server_ids, total = pipe.execute()
        servers = Play_servers.get(server_ids)
        return Pagination(
            page=page,
            per_page=per_page,
            total=total,
            records=servers,
        )

    @classmethod
    def has_access(cls, play_server_id, user_id):     
        '''

        :param play_server_id: int
        :param user_id: int
        :returns: bool
        '''
        return database.redis.sismember('play_server_user_access:{}'.format(
            play_server_id
        ), user_id)