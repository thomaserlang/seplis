import asyncio
from functools import partial
import logging
import signal
from seplis.config import config
import os
import tornado.web
from seplis.io_sighandler import sig_handler
import seplis.web.handlers.react
import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration
from .handlers import react, tvmaze_lookup, base, health
from seplis.logger import logger
from tornado.web import URLSpec

class Application(tornado.web.Application):

    def __init__(self, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=config.data.debug,
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret=config.data.web.cookie_secret,
            login_url='/sign-in',
        )
        urls = [
            URLSpec(r'/static/(.*)', base.File_handler, {'path': static_path}),
            URLSpec(r'/api/tvmaze-show-lookup', tvmaze_lookup.Handler),

            URLSpec(r'/show.*/([0-9]+)', react.Handler_series),
            URLSpec(r'/show/([0-9]+)/[^/]+', react.Handler_series),
            URLSpec(r'/show-edit/([0-9]+)', react.Handler_series),

            URLSpec(r'/movie.*/([0-9]+)', react.Handler_movie),
            URLSpec(r'/movie/([0-9]+)/[^/]+', react.Handler_movie),
            URLSpec(r'/movie-edit/([0-9]+)', react.Handler_movie),

            URLSpec(r'/health', health.Handler),
            URLSpec(r'/', react.Handler),
            URLSpec(r'/(.*)', react.Handler),

        ]
        super().__init__(urls, **settings)

async def main():
    logger.set_logger(f'web-{config.data.web.port}.log')
    if config.data.sentry_dsn:
        sentry_sdk.init(
            dsn=config.data.sentry_dsn,
            integrations=[TornadoIntegration()],
        )

    app = Application()
    server = app.listen(config.data.web.port)
    
    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))    

    log = logging.getLogger('main')
    log.setLevel('INFO')
    log.info(f'Web server started on port: {config.data.web.port}')
    await asyncio.Event().wait()
    log.info('Web server stopped')

if __name__ == '__main__':
    import seplis
    seplis.config_load()
    main()