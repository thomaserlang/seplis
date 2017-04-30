from seplis.config import config
import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import seplis.web.handlers.react
from .handlers import react, tvmaze_lookup
from seplis.logger import logger
from tornado.web import URLSpec

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
            login_url='/sign-in',
        )

        urls = [
            URLSpec(r'/favicon.ico', tornado.web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            URLSpec(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),

            URLSpec(r"/", tornado.web.RedirectHandler, {"url": "/main"}),
            URLSpec(r"/air-dates", tornado.web.RedirectHandler, {"url": "/main"}),


            URLSpec(r'/show-new', react.Handler),
            URLSpec(r'/show.*/([0-9]+)', react.Handler),
            URLSpec(r'/show/([0-9]+)/[^/]+', react.Handler),
            URLSpec(r'/show-edit/([0-9]+)', react.Handler),

            URLSpec(r'/fan-of', react.Handler),
            URLSpec(r'/main', react.Handler),
            URLSpec(r'/account', react.Handler),
            URLSpec(r'/password', react.Handler),
            URLSpec(r'/play-servers', react.Handler),
            URLSpec(r'/play-server', react.Handler),
            URLSpec(r'/show/([0-9]+)/episode/([0-9]+)/play', react.Handler_without_menu_no_container),

            URLSpec(r'/sign-in', react.Handler_without_menu),
            URLSpec(r'/create-user', react.Handler_without_menu),

            URLSpec(r'/api/tvmaze-show-lookup', tvmaze_lookup.Handler),
        ]
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    logger.set_logger('web-{}.log'.format(config['web']['port']))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['web']['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    import seplis
    seplis.config_load()
    main()