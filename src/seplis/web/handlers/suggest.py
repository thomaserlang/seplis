from seplis.web.handlers import base
from tornado import gen, escape

class Handler(base.Handler):

    @gen.coroutine
    def get(self):
        suggest = yield self.client.get('/suggest-shows?q={}'.format(
            escape.url_escape(self.get_argument('q'))
        ))
        self.write_object(suggest)