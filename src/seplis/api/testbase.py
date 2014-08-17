import os
import redis
from seplis.utils import json_dumps, json_loads
from urllib.parse import urlencode
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase
from seplis.config import config
from seplis.connections import database
from seplis.logger import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from seplis.api.app import Application
from seplis.api.base.app import App
from seplis.api.base.user import User, Token
from seplis.api import elasticcreate
from elasticsearch import Elasticsearch

class Testbase(AsyncHTTPTestCase):

    access_token = None
    current_user = None

    def get_app(self):
        return Application()

    def setUp(self):
        super(Testbase, self).setUp()
        import seplis.config
        seplis.config.load()
        config['logging']['path'] = None
        logger.set_logger('test.log')
        engine = create_engine(config['database']['url'], convert_unicode=True, echo=False)
        connection = engine.connect()
        self.trans = connection.begin()
        database.session = sessionmaker(bind=connection)
        database.redis = redis.StrictRedis(
            config['redis']['ip'], 
            port=config['redis']['port'], 
            db=10,
            decode_responses=True,
        )
        database.redis.flushdb()
        database.es = Elasticsearch(config['elasticsearch'])
        database.es.indices.delete(index='_all')
        elasticcreate.create_indices()

    def tearDown(self):
        self.trans.rollback()
        super(Testbase, self).tearDown()

    def _fetch(self, url, method, data=None, headers=None):
        full_url = url
        if 'http://' not in url:
            full_url = self.get_url(url)
        if data is not None:
            if isinstance(data, dict):
                data = json_dumps(data)
        if self.access_token and (headers == None):
            headers = {}
            headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        request = HTTPRequest(full_url, headers=headers, method=method, body=data)
        self.http_client.fetch(request, self.stop)
        return self.wait()

    def get(self, url, data={}, headers=None):
        if data is not None:
            if isinstance(data, dict):
                data = urlencode(data, True)
            if '?' in url:
                url += '&%s' % data
            else:
                url += '?%s' % data
        return self._fetch(url, 'GET', headers=headers)

    def post(self, url, data='', headers=None):
        return self._fetch(url, 'POST', data, headers)

    def put(self, url, data='', headers=None):
        return self._fetch(url, 'PUT', data, headers)

    def patch(self, url, data='', headers=None):
        return self._fetch(url, 'PATCH', data, headers)

    def delete(self, url, headers=None):
        return self._fetch(url, 'DELETE', headers)

    def login(self, user_level=0, app_level=0):
        if self.current_user:
            return
        self.current_user = User.new(
            name='testuser',
            email='test@example.com',
            level=user_level,
        )
        self.current_app = App.new(
            user_id=self.current_user.id,
            name='testbase app',
            redirect_uri='',
            level=app_level,
        )
        self.access_token = Token.new(
            user_id=self.current_user.id, 
            app_id=self.current_app.id,
        )

    def new_show(self):
        self.login(0)
        response = self.post('/1/shows')
        self.assertEqual(response.code, 201, response.body)
        show = json_loads(response.body)
        self.assertTrue(show['id'] > 0)
        return show['id']