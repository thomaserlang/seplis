from seplis.config import config
import tornado.web
import tornado.httpserver
import tornado.ioloop
import handlers.signin
import handlers.settings
import handlers.show
import handlers.tag
import handlers.suggest
import modules.menu
import modules.follow_button
import modules.tags
import os
from seplis.logger import logger
from tornado.options import define, options
from seplis.web.client import Async_client

class Application(tornado.web.Application):

    def __init__(self, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=static_path,
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret=config['web']['cookie_secret'],
            login_url='/signin',
            ui_modules=dict(
                menu=modules.menu.Module,
                follow_button=modules.follow_button.Module,
                tags=modules.tags.Module,
            )
        )
        urls = [
            tornado.web.URLSpec(r'/favicon.ico', tornado.web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            tornado.web.URLSpec(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),

            # (r'/signup', handlers.signup.Handler),
            tornado.web.URLSpec(r'/signin', handlers.signin.Handler),
            tornado.web.URLSpec(r'/settings', handlers.settings.Handler),

            tornado.web.URLSpec(r'/shows/([0-9]+)', handlers.show.Handler),
            tornado.web.URLSpec(r'/follow', handlers.show.Follow_handler),

            tornado.web.URLSpec(r'/suggest', handlers.suggest.Handler),

            tornado.web.URLSpec(r'/user-tags', handlers.tag.Relation_handler),
            tornado.web.URLSpec(r'/users/([0-9]+)/tags/shows', handlers.tag.Shows_handler, name='user_tagged_shows'),

        ]
        tornado.web.Application.__init__(self, urls, **settings)
        self.client = Async_client(
            url=config['web']['api_url'],
            client_id=config['web']['client_id'],
        )

def main():
    logger.set_logger('web-{}.log'.format(config['web']['port']))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['web']['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    import seplis.config
    seplis.config.load()
    main()