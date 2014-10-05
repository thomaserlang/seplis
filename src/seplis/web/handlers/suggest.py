from seplis.web.handlers import base
from tornado import gen, escape

class Handler(base.API_handler):

    @gen.coroutine
    def get(self):
        q = self.get_argument('q')
        suggest = yield self.client.get('/shows', {
            'q': 'title:"{0}" OR alternative_titles:"{0}"'.format(
                q
            ),
            'fields': 'title',
        })
        self.write_object(suggest)