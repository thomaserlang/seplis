import logging
from seplis.web.handlers import base
from seplis import utils, constants
from seplis.web.client import API_error
from seplis.api import exceptions
from tornado import gen, escape
from tornado.web import HTTPError, authenticated
from collections import OrderedDict

class Handler(base.Handler):

    @authenticated
    @gen.coroutine
    def get(self):
        shows = yield self.client.get('/users/{}/etw'.format(
            self.current_user.id,
        ))
        self.render('etw.html',
            title='ETW',
            menu_id='etw',
            shows=shows,
        )