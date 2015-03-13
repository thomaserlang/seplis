from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session
from seplis.api import exceptions, constants
from seplis.api import models
from seplis import schemas
from tornado import gen
from tornado.concurrent import run_on_executor

class Server_handler(base.Handler):

    @authenticated(0)
    @gen.coroutine
    def post(self, user_id):
        self.check_user_edit(user_id)
        ps = yield self.create(user_id)
        self.set_status(201)
        self.write_object(ps)

    @run_on_executor
    def create(self, user_id):
        data = self.validate(schemas.Play_server, required=True)
        with new_session() as session:
            ps = models.Play_server(
                user_id=user_id,
                name=data['name'],
                url=data['url'],
                secret=data['secret'],
            )
            session.add(ps)
            session.commit()
            return ps.serialize()

    @authenticated(0)
    @gen.coroutine
    def put(self, user_id, id_):
        ps = yield self.update(id_)
        self.write_object(ps)

    @run_on_executor
    def update(self, id_):
        data = self.validate(schemas.Play_server)
        with new_session() as session:
            ps = session.query(models.Play_server).filter(
                models.Play_server.id == id_,
            ).first()
            if not ps:
                raise exceptions.Not_found('play server not found')
            self.check_user_edit(ps.user_id)
            self.update_model(ps, data, overwrite=True)
            session.commit()
            return ps.serialize()

    @authenticated(0)
    @gen.coroutine
    def delete(self, user_id, id_):
        yield self.remove(id_)

    @run_on_executor
    def remove(self, id_):
        with new_session() as session:
            ps = session.query(models.Play_server).filter(
                models.Play_server.id == id_,
            ).first()
            if not ps:
                raise exceptions.Not_found('play server not found')
            self.check_user_edit(ps.user_id)
            session.delete(ps)
            session.commit()

    @authenticated(0)
    def get(self, user_id, id_=None):
        if id_:
            server = models.Play_server.get(id_)
            if not server:
                raise exceptions.Not_found('the play server was not found')
            if server['user_id'] != self.current_user.id and \
                models.Play_server.has_access(server['id'], self.current_user.id):
                server.pop('secret')
            else:
                self.check_user_edit(server['user_id'])
            self.write_object(server)
        else:
            access_to = self.get_argument('access_to', False)
            if access_to == 'true':# get the servers that the user has access to
                servers = self.get_access_to_servers(user_id)
            else:# get the users own servers
                servers = self.get_servers(user_id)
            self.write_object(servers)

    def get_servers(self, user_id, access_to=False):
        self.check_user_edit(user_id)
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        servers = models.Play_server.by_user_id(
            user_id=user_id,
            access_to=access_to,
            page=page,
            per_page=per_page,
        )
        return servers

    def get_access_to_servers(self, user_id):
        servers = self.get_servers(user_id, access_to=True)
        for server in servers.records:
            server.pop('secret')
        return servers


class Access_handler(base.Handler):

    @authenticated(0)
    def get(self, user_id, server_id):
        self.check_user_edit(user_id)
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        users = models.Play_server.users_with_access(
            server_id,
            page=page,
            per_page=per_page,
        )
        self.write_object(users)

    def check_server(self, server_id):
        server = models.Play_server.get(server_id)
        if not server:
            raise exceptions.Unknown_play_server()
        self.check_user_edit(server['user_id'])

    @authenticated(0)
    @gen.coroutine
    def put(self, user_id, server_id, access_user_id):
        yield self.give_access(server_id, access_user_id)

    @run_on_executor
    def give_access(self, server_id, access_user_id):
        self.check_server(server_id)
        models.Play_server.give_access(
            id_=server_id,
            user_id=access_user_id,
        )

    @authenticated(0)
    @gen.coroutine
    def delete(self, user_id, server_id, access_user_id):
        yield self.remove_access(server_id, access_user_id)

    @run_on_executor
    def remove_access(self, server_id, access_user_id):
        self.check_server(server_id)
        models.Play_server.remove_access(
            id_=server_id,
            user_id=access_user_id,
        )