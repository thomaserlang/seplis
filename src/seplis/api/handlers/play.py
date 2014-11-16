from seplis.api.handlers import base
from seplis.api.base.play import Play_server, Play_servers, Play_user_access
from seplis.api.decorators import authenticated
from seplis.api import exceptions, constants
from seplis import schemas

class Handler(base.Handler):

    def get_server(self, id_):
        server = Play_server.get(id_)
        if not server:
            raise exceptions.Not_found('the play server was not found')
        self.check_user_edit(server.user_id)
        return server

class Server_handler(Handler):

    @authenticated(0)
    def post(self, user_id):
        self.check_user_edit(user_id)
        data = self.validate(schemas.Play_server, required=True)
        server = Play_server.new(
            user_id=user_id,
            name=data['name'],
            url=data['url'],
            secret=data['secret'],
        )
        self.set_status(201)
        self.write_object(server)

    @authenticated(0)
    def put(self, user_id, id_):
        server = self.get_server(id_)
        data = self.validate(schemas.Play_server)
        if 'name' in data:
            server.name = data['name']
        if 'url' in data:
            server.url = data['url']
        if 'secret' in data:
            server.secret = data['secret']
        server.save()
        self.write_object(server)

    @authenticated(0)
    def delete(self, user_id, id_):
        server = self.get_server(id_)
        server.delete()

    @authenticated(0)
    def get(self, user_id, id_=None):
        if id_:
            server = self.get_server(id_)
            self.write_object(server)
        else:
            access_to = self.get_argument('access_to', None)
            if access_to == 'true':# get the servers that the user has access to
                self.get_access_to_servers(user_id)
            else:# get the users own servers
                self.get_servers(user_id)

    def get_servers(self, user_id):
        self.check_user_edit(user_id)
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        servers = Play_servers.get_by_user_id(
            user_id=user_id,
            page=page,
            per_page=per_page,
        )
        self.write_object(servers)

    def get_access_to_servers(self, user_id):
        self.check_user_edit(user_id)
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        servers = Play_user_access.get_servers(
            user_id=user_id,
            page=page,
            per_page=per_page,
        )
        for server in servers.records:
            server.__dict__.pop('secret')
        self.write_object(servers)


class Access_handler(Handler):

    @authenticated(0)
    def get(self, user_id, server_id):
        self.check_user_edit(user_id)
        users = Play_server.get_users(server_id)
        self.write_object(users)

    @authenticated(0)
    def put(self, user_id, server_id, access_user_id):
        server = self.get_server(server_id)
        Play_user_access.add(
            play_server_id=server_id,
            user_id=access_user_id,
        )

    @authenticated(0)
    def delete(self, user_id, server_id, access_user_id):
        server = self.get_server(server_id)
        Play_user_access.delete(
            play_server_id=server_id,
            user_id=access_user_id,
        )