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
        episodes = yield self.client.get('/users/{}/air-dates'.format(
            self.current_user['id'],
        ))
        episodes = yield episodes.all_async()

        air_dates = OrderedDict()
        for episode in episodes:
            air_date = air_dates.setdefault(
                episode['episode']['air_date'],
                []
            )
            air_date.append(episode)

        self.render('air_dates.html',
            title='Air dates',
            air_dates=air_dates,
        )