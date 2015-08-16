import logging
from seplis.web.handlers import base
from seplis.api import exceptions
from seplis import utils, constants
from tornado import gen, escape
from tornado.web import HTTPError, authenticated

class Users_handler(base.API_handler):

    @gen.coroutine
    def get(self):
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', '_score')
        users = yield self.client.get(
            '/users',
            dict(
                q=self.get_argument('q', ''),
                sort=sort,
                page=page,
            )
        )
        self.write_object(users)