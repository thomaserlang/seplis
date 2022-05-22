import asyncio, logging, os, pytest

from sqlalchemy import create_engine
from seplis import config, config_load, utils
from seplis.utils import  json_loads
from urllib.parse import urlencode
from tornado.testing import AsyncHTTPTestCase
from seplis.api.connections import database
from seplis.api.app import Application
from seplis.api import elasticcreate, constants, models
from seplis.api.decorators import new_session

def run_file(file_):
    pytest.main([
        '-o', 'log_cli=true', 
        '-o', 'log_cli_level=debug',
        '-o', 'log_cli_format=%(asctime)s.%(msecs)3d %(filename)-15s %(lineno)4d %(levelname)-8s %(message)s',
        file_,
    ])

class Testbase(AsyncHTTPTestCase):

    access_token = None
    current_user = None

    def get_app(self):
        return Application()

    def setUp(self):
        super().setUp()
        logger = logging.getLogger('elasticsearch')
        logger.setLevel(logging.ERROR)
        logger = logging.getLogger('urllib3')
        logger.setLevel(logging.ERROR)
        # recreate the database connection
        # with params from the loaded config.
        connection = database.engine.connect()
        self.trans = connection.begin()
        database.setup_sqlalchemy_session(connection)
        loop = asyncio.get_event_loop()
        connection = loop.run_until_complete(database.async_engine.connect())
        self.trans_async = loop.run_until_complete(connection.begin())
        database.setup_sqlalchemy_async_session(connection)

        database.redis.flushdb()
        elasticcreate.create_indices()

    def tearDown(self):
        self.trans.rollback()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.trans_async.rollback())
        super().tearDown()

    @classmethod
    def setUpClass(cls):
        config_load()
        config['debug'] = False
        config['logging']['path'] = None

        if hasattr(database, 'async_engine'):
            return
        
        from sqlalchemy.engine import url
        u = url.make_url(config['api']['database_test'])
        db = u.database
        u = url.URL.create(
            drivername='mysql+pymysql',
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
        cfg.set_main_option('sqlalchemy.url', config['api']['database_test'])
        command.upgrade(cfg, 'head')

        database.connect(config['api']['database_test'], redis_db=15)


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
        self.get('http://{}/_refresh'.format(
            config['api']['elasticsearch']
        ))

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