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
        air_dates = yield self.client.get('/users/{}/air-dates'.format(
            self.current_user.id,
        ))
        recently_watched = yield self.client.get('/users/{}/shows-recently-watched'.format(
            self.current_user.id
        ), {
            'per_page': 5
        })
        self.render('air_dates.html',
            title='Air dates',
            air_dates=air_dates,
            recently_watched=recently_watched,
        )