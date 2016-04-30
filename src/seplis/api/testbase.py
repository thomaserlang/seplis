import os
import redis
import logging
from seplis import config, config_load, utils
from seplis.utils import json_dumps, json_loads
from urllib.parse import urlencode
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase
from seplis.api.connections import database, setup_event_listeners
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from seplis.api.app import Application
from seplis.api import elasticcreate, constants, models
from seplis.api.decorators import new_session
from elasticsearch import Elasticsearch

class Testbase(AsyncHTTPTestCase):

    access_token = None
    current_user = None

    def get_app(self):
        return Application()

    def setUp(self):
        super(Testbase, self).setUp()
        config_load()
        config['logging']['path'] = None
        logger = logging.getLogger('raven')
        logger.setLevel(logging.ERROR)
        # recreate the database connection
        # with params from the loaded config.
        database.__init__()
        connection = database.engine.connect()
        self.trans = connection.begin()
        database.session = sessionmaker(bind=connection)
        setup_event_listeners(database.session)
        database.redis.flushdb()
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
        if self.access_token:
            if headers == None:
                headers = {}
            if 'Authorization' not in headers:
                headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        request = HTTPRequest(full_url, headers=headers, method=method, body=data)
        self.http_client.fetch(request, self.stop)
        return self.wait()

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
        self.login(constants.LEVEL_EDIT_SHOW)
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