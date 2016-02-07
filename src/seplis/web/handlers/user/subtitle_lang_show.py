import logging
from seplis.web.handlers import base
from seplis.api import exceptions
from seplis import utils, constants
from tornado import gen, escape
from tornado.web import HTTPError, authenticated

class API_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def get(self):
        show_id = self.get_argument('show_id')
        data = yield self.client.get('/users/{}/subtitle-lang/shows/{}'.format(
            self.current_user.id,
            show_id,
        ))
        if data:
            self.write_object(data)
        else:
            self.write('{}')

    @authenticated
    @gen.coroutine
    def post(self):
        show_id = self.get_argument('show_id')
        subtitle_lang = self.get_argument('subtitle_lang', None)
        audio_lang = self.get_argument('audio_lang', None)
        data = yield self.client.put('/users/{}/subtitle-lang/shows/{}'.format(
            self.current_user.id,
            show_id,
        ), {
            'subtitle_lang': subtitle_lang if subtitle_lang else None,
            'audio_lang': audio_lang if audio_lang else None,
        })
        self.write('{}')