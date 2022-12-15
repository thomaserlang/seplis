import asyncio, logging, os, pytest, pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine, insert, select
from seplis import config, config_load, utils
from seplis.utils import  json_loads
from urllib.parse import urlencode
from tornado.testing import AsyncHTTPTestCase
from seplis.api.app import Application
from seplis.api import elasticcreate, constants, models
from seplis.api.decorators import new_session

from fastapi.testclient import TestClient
from seplis.api.main import app
from seplis.api.database import database
from seplis.api import schemas
from seplis import logger

@pytest_asyncio.fixture(scope='function')
async def client():
    config.data.test = True
    await database.setup_test()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    await database.close_test()

async def user_signin(client: AsyncClient, scopes: list[str] = [str(constants.LEVEL_USER)], app_level=constants.LEVEL_GOD) -> int:
    user = await models.User.save(user_data=schemas.User_create(
        username='testuser',
        email='test@example.com',
        level=int(scopes[0]),
        password='1'*10,
    ))
    token = await models.Token.new_token(user_id=user.id, expires_days=1, user_level=int(scopes[0]))
    client.headers['Authorization'] = f'Bearer {token}'
    return user.id

def run_file(file_):
    import subprocess
    subprocess.call(['pytest', '--tb=short', str(file_)])

class Testbase(AsyncHTTPTestCase):
    async_conn = None
    access_token = None
    current_user = None

    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        from tornado.ioloop import IOLoop
        return IOLoop.current()

    def setUp(self):
        super().setUp()
        # recreate the database connection
        # with params from the loaded config.data.
        connection = database.engine.connect()
        self.trans = connection.begin()
        database.setup_sqlalchemy_session(connection)
        self.loop = asyncio.get_event_loop()
        self.async_conn = self.loop.run_until_complete(database.async_engine.connect())
        database.setup_sqlalchemy_async_session(self.async_conn)
        self.trans_async = self.loop.run_until_complete(self.async_conn.begin())

        database.redis.flushdb()
        elasticcreate.create_indices()

    def tearDown(self):
        self.trans.rollback()
        self.loop.run_until_complete(self.trans_async.rollback())
        self.loop.run_until_complete(self.async_conn.close())
        super().tearDown()

    @classmethod
    def setUpClass(cls):
        config_load()
        config.data.debug = False
        config.data.logging.path = None

        if hasattr(database, 'async_engine'):
            return
        
        from sqlalchemy.engine import url
        u = url.make_url(config.data.api.database_test)
        db = u.database
        u = url.URL.create(
            drivername='mariadb+pymysql',
            username=u.username,
            password=u.password,
            host=u.host,
            port=u.port,
        )
        engine = create_engine(u)
        engine.execute(f'CREATE SCHEMA IF NOT EXISTS {db} DEFAULT CHARACTER SET utf8mb4;')
        engine.dispose()

        from alembic.config import Config
        from alembic import command
        cfg = Config(os.path.dirname(os.path.abspath(__file__))+'/alembic.ini')
        cfg.set_main_option('script_location', 'seplis.api:migration')
        cfg.set_main_option('sqlalchemy.url', config.data.api.database_test)
        command.upgrade(cfg, 'head')

        database.connect(config.data.api.database_test, redis_db=15)


    def _fetch(self, url, method, data=None, headers=None):
        if data is not None:
            if isinstance(data, dict) or isinstance(data, list):
                data = utils.json_dumps(data)
        if self.access_token:
            if headers == None:
                headers = {}
            if 'Authorization' not in headers:
                headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        return self.fetch(url, headers=headers, method=method, body=data)

    def get(self, url, data={}, headers=None):
        if data != None:
            if isinstance(data, dict):
                data = urlencode(data, True)
            url += '{}{}'.format(
                '&' if '?' in url else '?', 
                data
            )
        return self._fetch(url, 'GET', headers=headers)

    def post(self, url, data='', headers=None):
        return self._fetch(url, 'POST', data, headers)

    def put(self, url, data='', headers=None):
        return self._fetch(url, 'PUT', data, headers)

    def patch(self, url, data='', headers=None):
        return self._fetch(url, 'PATCH', data, headers)

    def delete(self, url, headers=None):
        return self._fetch(url, 'DELETE', headers)

    def login(self, user_level=0, app_level=constants.LEVEL_GOD):
        if self.current_user:
            return
        with new_session() as session:
            user = models.User(
                name='testuser',
                email='test@example.com',
                level=user_level,
            )
            session.add(user)
            session.flush()
            self.current_user = utils.dotdict(user.serialize())
            app = models.App(
                user_id=user.id,
                name='testbase app',
                redirect_uri='',
                level=app_level,
            )
            session.flush()
            self.current_app = utils.dotdict(app.serialize())
            access_token = models.Token(
                user_id=user.id,
                user_level=user_level,
                app_id=app.id,
            )
            session.add(access_token)
            session.commit()
            self.access_token = access_token.token

    def login_async(self, user_level=0, app_level=constants.LEVEL_GOD):
        async def login():
            async with database.async_session() as session:
                r = await session.execute(insert(models.User).values(
                    name='testuser',
                    email='test@example.com',
                    level=user_level,
                ))
                user = await session.scalar(select(models.User).where(models.User.id == r.lastrowid))
                self.current_user = utils.dotdict(user.serialize())
                for key in self.current_user:
                    database.redis.hset(f'users:{self.current_user.id}', key, self.current_user[key] if self.current_user[key] != None else 'None')

                r = await session.execute(insert(models.App).values(
                    user_id=user.id,
                    name='testbase app',
                    redirect_uri='',
                    level=app_level,
                ))
                app = await session.scalar(select(models.App).where(models.App.id == r.lastrowid))
                self.current_app = utils.dotdict(app.serialize())

                token = utils.random_key()
                r = await session.execute(insert(models.Token).values(
                    user_id=user.id,
                    user_level=user_level,
                    app_id=app.id,
                    token=token,
                ))
                self.access_token = token
                database.redis.hset(f'tokens:{token}', 'user_id', self.current_user.id)
                database.redis.hset(f'tokens:{token}', 'user_level', user_level)
                await session.commit()
        asyncio.get_event_loop().run_until_complete(login())

    def new_show(self):
        '''Signs the user in and returns a show id.
        :returns: int (show_id)
        '''
        self.login(constants.LEVEL_GOD)
        response = self.post('/1/shows', {
            'status': 1,
        })
        self.assertEqual(response.code, 201, response.body)
        show = json_loads(response.body)
        self.assertTrue(show['id'] > 0)        
        self.refresh_es()
        return show['id']

    def refresh_es(self):
        database.es.indices.refresh()

    def new_app(self, name, user_id, level, redirect_uri=''):
        with new_session() as session:
            app = models.App(
                name=name,
                user_id=user_id,
                level=level,
                redirect_uri='',
            )
            session.add(app)
            session.commit()
            return utils.dotdict(app.serialize())

    def new_user(self, name, email, level, password=''):
        with new_session() as session:
            user = models.User(
                name=name,
                email=email,
                password=password,
                level=level,
            )
            session.add(user)
            session.commit()
            return utils.dotdict(user.serialize())

    def execute_query(self, query):
        async def run():
            with database.async_engine() as session:
                r = await session.execute(query)
                await session.commit()
                return r
        return self.loop.run_until_complete(run())

    def with_session(self, f, **kwargs):
        async def run():
            async with database.async_session() as session:
                r = await f(session=session, **kwargs)
                await session.commit()
                return r
        return self.loop.run_until_complete(run())