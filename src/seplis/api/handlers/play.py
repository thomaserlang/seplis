from seplis.api.handlers import base
from seplis.api.base.play import Play_server, Play_user_access
from seplis.api.decorators import authenticated
from seplis.api import exceptions
from seplis import schemas

class Handler(base.Handler):

    @authenticated(0)
    def post(self, user_id):
        self.check_user_edit(user_id)
        data = self.validate(schemas.Play_server, required=True)
        server = Play_server.new(
            user_id=user_id,
            name=data['name'],
            address=data['address'],
        )
        self.ser_status(201)
        self.write_object(server)

    @authenticated(0)
    def put(self, user_id, id_):        
        self.check_user_edit(user_id)
        server = Play_server.get(id_)
        if not server:
            raise exceptions.Not_found('the play server was not found')
        if server.user_id !=
        data = self.validate(schemas.Play_server)
        if 'name' in data:
            server.name = name
        if 'address' in data:
            server.address = address
        server.save()
        self.write_object(server)

    @authenticated(0)
    def delete(self, user_id, id_):
        