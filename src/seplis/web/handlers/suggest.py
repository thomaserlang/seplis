from seplis.web.handlers import base
from tornado import gen, escape

class Handler(base.API_handler):

    @gen.coroutine
    def get(self):
        suggest = yield self.client.get('/shows', {
            'q': self.get_argument('q'),
            'fields': 'title'
        })
        self.write_object(suggest)