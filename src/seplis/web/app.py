import asyncio
from functools import partial
import logging
import signal
from seplis import health
from seplis.config import config
import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
from seplis.io_sighandler import sig_handler
import seplis.web.handlers.react
import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration
from .handlers import react, tvmaze_lookup, base
from seplis.logger import logger
from tornado.web import URLSpec

class Application(tornado.web.Application):

    def __init__(self, ioloop=None, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret=config['web']['cookie_secret'],
            login_url='/sign-in',
        )
        self.ioloop = ioloop or asyncio.get_event_loop()
        urls = [
            URLSpec(r'/static/(.*)', base.File_handler, {'path': static_path}),
            URLSpec(r'/api/tvmaze-show-lookup', tvmaze_lookup.Handler),

            URLSpec(r'/show.*/([0-9]+)', react.Handler_tv_show),
            URLSpec(r'/show/([0-9]+)/[^/]+', react.Handler_tv_show),
            URLSpec(r'/show-edit/([0-9]+)', react.Handler_tv_show),

            URLSpec(r'/health', health.Handler),
            URLSpec(r'/', react.Handler),
            URLSpec(r'/(.*)', react.Handler),

        ]
        super().__init__(urls, **settings)

def main():
    ioloop = asyncio.get_event_loop()
    app = Application(ioloop)
    logger.set_logger('web-{}.log'.format(config['web']['port']))
    if config['sentry_dsn']:
        sentry_sdk.init(
            dsn=config['sentry_dsn'],
            integrations=[TornadoIntegration()],
        )
    server = tornado.httpserver.HTTPServer(app)
    server.listen(config['web']['port'])
    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))    
    logging.info(f'Web server started on port: {config["web"]["port"]}')
    ioloop.run_forever()

if __name__ == '__main__':
    import seplis
    seplis.config_load()
    main()