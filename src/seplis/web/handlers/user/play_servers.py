import logging
from seplis.web.handlers import base
from seplis.api import exceptions
from seplis import utils, constants
from tornado import gen, escape
from tornado.web import HTTPError, authenticated

class Handler(base.Handler):

    @authenticated
    @gen.coroutine
    def get(self):
        play_servers = yield self.client.get('/users/{}/play-servers'.format(
            self.current_user['id'],
        ))
        self.render(
            'user/play_servers.html',
            title='Play servers',
            play_servers=play_servers,
        )

class Form_handler(base.Handler):

    @authenticated
    @gen.coroutine
    def get(self):
        id_ = self.get_argument('id', None)
        play_server = None
        play_users = None
        if id_:
            play_server = yield self.client.get('/users/{}/play-servers/{}'.format(
                self.current_user['id'],
                id_,
            ))
            if not play_server:
                raise HTTPError(404, 'unknown play server')
            play_users = yield self.client.get(
                '/users/{}/play-servers/{}/users'.format(
                    self.current_user['id'],
                    id_,
                ))
        self.render(
            'user/play_server_form.html',
            play_server=play_server,
            play_users=play_users,
        )

class API_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def post(self):
        id_ = self.get_argument('id', None)
        data = {
            'name': self.get_argument('name'),
            'url': self.get_argument('url'),
            'secret': self.get_argument('secret'),
        }
        if id_:
            ps = yield self.client.put('/users/{}/play-servers/{}'.format(
                self.current_user['id'],
                id_,
            ), data)
        else:
            ps = yield self.client.post('/users/{}/play-servers'.format(
                self.current_user['id'],
            ), data)
        self.write_object(ps)

    @authenticated
    @gen.coroutine
    def delete(self):
        yield self.client.delete('/users/{}/play-servers/{}'.format(
            self.current_user['id'],
            self.get_argument('id'),
        ))
        self.write('{}')

class API_user_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def post(self):
        yield self.client.put('/users/{}/play-servers/{}/users/{}'.format(
            self.current_user['id'],
            self.get_argument('server_id'),
            self.get_argument('user_id'),
        ))
        self.write('{}')

    @authenticated
    @gen.coroutine
    def delete(self):
        yield self.client.delete('/users/{}/play-servers/{}/users/{}'.format(
            self.current_user['id'],
            self.get_argument('server_id'),
            self.get_argument('user_id'),
        ))
        self.write('{}')