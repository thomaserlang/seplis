from tornado.web import HTTPError
from tornado.httpclient import AsyncHTTPClient
from seplis.web.handlers import base
from seplis import utils, constants

class Handler(base.API_handler):

    async def get(self):
        httpclient = AsyncHTTPClient()
        tvmaze = self.get_argument('tvmaze', None)
        if tvmaze:
            url = 'http://api.tvmaze.com/shows/{}'.format(tvmaze)
        else:
            url = 'http://api.tvmaze.com/lookup/shows?{}'.format(
                utils.url_encode_tornado_arguments(self.request.arguments)
            )
        response = await httpclient.fetch(url)
        if 200 <= response.code <= 399: 
            self.write(response.body)
        else:
            raise HTTPError(code, response.body)