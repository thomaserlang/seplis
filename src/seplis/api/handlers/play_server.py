import good
import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import exceptions, constants, models
from seplis import schemas

_schema = {
    'name': good.All(str, good.Length(min=1, max=45)),
    'url': good.All(str, good.Length(min=1, max=200)),
    'secret': good.All(str, good.Length(min=1, max=200)),
}

class Handler(base.Handler):
    '''Edit a play server. The user must be the owner.'''

    __schema__ = good.Schema(_schema, default_keys=good.Optional)

    @authenticated(0)
    async def get(self, id_):
        server = await self._get(id_)
        self.write_object(server)

    @authenticated(0)
    async def put(self, id_):
        ps = await self._put(id_)
        self.write_object(ps)

    @authenticated(0)
    async def delete(self, id_):
        await self._delete(id_)
        self.set_status(204)

    @run_on_executor
    def _get(self, id_):
        with new_session() as session:
            q = session.query(models.Play_server).filter(
                models.Play_server.id == id_,
                models.Play_server.user_id == self.current_user.id,
            ).options(sa.orm.undefer_group('secret')).first()
            if not q:
                raise exceptions.Not_found('play server not found')
            return q.serialize()

    @run_on_executor
    def _put(self, id_):
        data = self.validate()
        if 'url' in data:
            data['url'] = data['url'].rstrip('/')
        with new_session() as session:
            ps = session.query(models.Play_server).filter(
                models.Play_server.id == id_,
                models.Play_server.user_id == self.current_user.id,
            ).options(sa.orm.undefer_group('secret')).first()
            if not ps:
                raise exceptions.Not_found('play server not found')
            self.update_model(ps, data, overwrite=True)
            session.commit()
            ps = session.query(models.Play_server).options(
                sa.orm.undefer_group('secret')
            ).get(ps.id)
            return ps.serialize()

    @run_on_executor
    def _delete(self, id_):
        with new_session() as session:
            ps = session.query(models.Play_server).filter(
                models.Play_server.id == id_,
                models.Play_server.user_id == self.current_user.id,
            ).first()
            if not ps:
                raise exceptions.Not_found('play server not found')
            session.delete(ps)
            session.commit()

class Collection_handler(base.Pagination_handler):
    '''List of play servers that the user is owner of'''

    __schema__ = good.Schema(_schema)

    @authenticated(0)
    async def get(self):
        super().get()
        servers = await self._get()
        self.write_object(servers)

    @authenticated(0)
    async def post(self):
        ps = await self._post()
        self.set_status(201)
        self.write_object(ps)

    @run_on_executor
    def _get(self):
        with new_session() as session:
            p = session.query(models.Play_server).filter(
                models.Play_server.user_id == self.current_user.id,
            ).order_by(models.Play_server.name).paginate(
                page=self.page, per_page=self.per_page,
            )
            p.records = [r.serialize() for r in p.records]
            return p

    @run_on_executor
    def _post(self):
        data = self.validate()
        if 'url' in data:
            data['url'] = data['url'].rstrip('/')
        with new_session() as session:
            ps = models.Play_server(
                user_id=self.current_user.id,
                **data
            )
            session.add(ps)
            session.commit()
            ps = session.query(models.Play_server).options(
                sa.orm.undefer_group('secret')
            ).get(ps.id)
            return ps.serialize()

class Access_handler(base.Pagination_handler):
    ''' Get a list of users with access or 
    give a user access to a play server.
    '''

    @authenticated(0)
    async def get(self, server_id):
        super().get()
        d = await self._get(server_id)
        self.write_object(d)

    @authenticated(0)
    async def put(self, server_id, access_user_id):
        await self._put(server_id, access_user_id)
        self.set_status(204)

    @authenticated(0)
    async def delete(self, server_id, access_user_id):
        await self._delete(server_id, access_user_id)
        self.set_status(204)

    @run_on_executor
    def _get(self, server_id):
        with new_session() as session:
            users = session.query(models.User).filter(
                models.Play_server.id == server_id,
                models.Play_server.user_id == self.current_user.id,
                models.Play_access.play_server_id == models.Play_server.id,
                models.User.id == models.Play_access.user_id,
            ).order_by(models.User.name).paginate(
                page=self.page, per_page=self.per_page,
            )
            print(users.records)
            a = []
            for u in users.records:
                a.append({
                    'name': u.name,
                    'id': u.id,
                    'fan_of': u.fan_of,
                    'created_at': u.created_at,
                })
            users.records = a
            return users

    @run_on_executor
    def _put(self, server_id, access_user_id):
        with new_session() as session:
            self.check_server(session, server_id)
            ac = models.Play_access(
                play_server_id=server_id,
                user_id=access_user_id,
            )
            session.merge(ac)
            session.commit()

    @run_on_executor
    def _delete(self, server_id, access_user_id):
        with new_session() as session:
            self.check_server(session, server_id)
            ac = session.query(models.Play_access).filter(
                models.Play_access.play_server_id == models.Play_server.id,
                models.Play_access.user_id == access_user_id,
            ).first()
            if ac:
                session.delete(ac)
            session.commit()

    def check_server(self, session, server_id):
        server = session.query(models.Play_server).get(server_id)
        if not server:
            raise exceptions.Unknown_play_server()
        if server.user_id != self.current_user.id:
            raise exceptions.Forbidden('You must be the owner')