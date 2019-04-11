from seplis.config import config
import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import seplis.web.handlers.react
from .handlers import react, tvmaze_lookup, base
from seplis.logger import logger
from tornado.web import URLSpec

class Application(tornado.web.Application):

    def __init__(self, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret=config['web']['cookie_secret'],
            login_url='/sign-in',
        )
        urls = [
            URLSpec(r'/static/(.*)', base.File_handler, {'path': static_path}),
            URLSpec(r'/api/tvmaze-show-lookup', tvmaze_lookup.Handler),

            URLSpec(r'/show.*/([0-9]+)', react.Handler_tv_show),
            URLSpec(r'/show/([0-9]+)/[^/]+', react.Handler_tv_show),
            URLSpec(r'/show-edit/([0-9]+)', react.Handler_tv_show),

            URLSpec(r'/', react.Handler),
            URLSpec(r'/(.*)', react.Handler),

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