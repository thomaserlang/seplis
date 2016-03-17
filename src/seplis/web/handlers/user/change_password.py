import logging
from seplis.web.handlers import base
from seplis.api import exceptions
from seplis import utils, constants
from tornado import gen, escape
from tornado.web import HTTPError, authenticated

class Handler(base.Handler):

    @authenticated
    def get(self):
        self.render('user/change_password.html',
            title='Change password',
        )

class API_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def post(self):
        yield self.client.post('/users/current/change-password', {
            'password': self.get_argument('password'),
            'new_password': self.get_argument('new-password'),
        })
        self.write_object({})