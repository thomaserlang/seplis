from seplis.web.handlers import base
from tornado import gen, escape

class Handler(base.API_handler):

    @gen.coroutine
    def get(self):
        q = self.get_argument('q')
        suggest = yield self.client.get('/shows', {
            'q': 'title.suggest:"{0}" OR alternative_titles.suggest:"{0}"'.format(
                q
            ),
            'per_page': 5,
            'fields': 'title,poster_image,premiered',
        })
        self.write_object(suggest)