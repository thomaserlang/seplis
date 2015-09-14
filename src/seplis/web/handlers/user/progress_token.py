import logging
from seplis.web.handlers import base
from seplis.api import exceptions, models
from seplis.api.decorators import new_session
from seplis import utils, constants, config
from tornado import gen, escape
from tornado.web import HTTPError, authenticated
from tornado.concurrent import run_on_executor
from datetime import datetime, timedelta

class API_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def get(self):
        d = yield self.client.get('/progress-token')
        d.data['api_url'] = config['client']['public_api_url']
        d.data['user_id'] = self.current_user['id']
        self.write_object(d)