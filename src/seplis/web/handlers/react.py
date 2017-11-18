from tornado import web
from seplis.web.handlers import base
from seplis.web import client
from seplis import utils, config

class Handler(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react.html')

class Handler_without_menu(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react_without_menu.html')

class Handler_without_menu_no_container(base.Handler_unauthenticated):

    def get(self, *args, **kwargs):
        self.render('react_without_menu_no_container.html')

class Handler_tv_show(base.Handler_unauthenticated):

    async def get(self, show_id):        
        c = client.Async_client(config['client']['api_url'], version='1')
        show = await c.get('/shows/{}'.format(show_id))
        if not show:
            raise web.HTTPError(404, 'Unknown show')
        self.render('react_tv_show.html', show=show, utils=utils)