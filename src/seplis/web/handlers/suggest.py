from seplis.web.handlers import base
from tornado import gen, escape

class Handler(base.API_handler):

    @gen.coroutine
    def get(self):
        q = self.get_argument('q')
        suggest = yield self.client.get('/shows', {
            'title_suggest': q,
            'per_page': 10,
            'fields': 'title,poster_image,premiered',
        })
        self.write_object(suggest)