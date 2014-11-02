from seplis.api import models
from seplis.decorators import auto_session, auto_pipe
from seplis import connections
from datetime import datetime

class Play_server(object):

    def __init__(self, id, created, updated, user_id, name,
        address):
        '''

        :param id: int
        :param created: datetime
        :param updated: datetime
        :param user_id: int
        :param name: str
        :param address: str
        '''
        self.id = id
        self.created = created
        self.updated = updated
        self.user_id = user_id
        self.name = name
        self.address = address

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
        )

    @classmethod
    @auto_session
    def new(cls, user_id, name, address, session=None):
        server = models.Play_server(
            user_id=user_id,
            name=name,
            address=address,
            created=datetime.utcnow(),
        )
        session.add(server)
        session.flush()
        return cls._format_from_row(server)

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
        ps = Play_server(
            id=int(server.id),
            created=server.created,
            edited=server.edited,
            user_id=int(server.user_id),
            name=server.name,
            address=server.address,
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

class Play_user_access(object):

    @classmethod
    @auto_session
    @auto_pipe
    def add(cls, play_server_id, user_id, session=None, pipe=None):
        pa = models.Play_access(
            play_server_id=play_server_id,
            user_id=user_id,
        )
        session.merge(pa)
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
    def delete(cls, play_server_id, user_id, session=None):
        '''

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