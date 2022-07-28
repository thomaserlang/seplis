from tornado import web
from seplis.web.handlers import base
from seplis.web import client
from seplis import utils, config

class Handler(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('ui/react.html')

class Handler_series(base.Handler_unauthenticated):

    async def get(self, series_id):        
        c = client.Async_client(config.data.client.api_url, version='1')
        series = await c.get(f'/shows/{series_id}')
        if not series:
            raise web.HTTPError(404, 'Unknown series')
        self.render('series.html', series=series, utils=utils)


class Handler_movie(base.Handler_unauthenticated):

    async def get(self, movie_id):        
        c = client.Async_client(config.data.client.api_url, version='1')
        movie = await c.get(f'/movies/{movie_id}')
        if not movie:
            raise web.HTTPError(404, 'Unknown movie')
        self.render('movie.html', movie=movie, utils=utils)