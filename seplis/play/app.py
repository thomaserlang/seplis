import asyncio
from functools import partial
import logging
import signal
from seplis.io_sighandler import sig_handler
from seplis.play.handlers import play, shows, health
import tornado.web
import os, os.path
from seplis import config
from seplis.logger import logger

class Application(tornado.web.Application):

    def __init__(self, ioloop=None, **args):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=config.data.debug,
            autoescape=None,
            xsrf_cookies=False,
        )
        self.ioloop = ioloop or asyncio.get_event_loop()
        urls = [
            (r'/transcode', play.Transcode_handler),
            (r'/subtitle-file', play.Subtitle_file_handler),
            (r'/source', play.Source_handler),
            (r'/sources', play.Sources_handler),
            (r'/files/(.*)', play.File_handler),
            (r'/close-session/(.*)', play.Close_session_handler),
            (r'/keep-alive/(.*)', play.Keep_alive_handler),

            (r'/', shows.Handler),
            (r'/api/show-suggest', shows.API_show_suggest_handler),
            (r'/health', health.Handler),
        ]
        super().__init__(urls, **settings)

def main():
    logger.set_logger(f'play_server_{config.data.play.port}.log')
    loop = asyncio.get_event_loop()
    app = Application(loop)
    server = app.listen(config.data.play.port)

    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))
    
    log = logging.getLogger('main')
    log.setLevel('INFO')
    log.info(f'Play server started on port: {config.data.play.port}')
    loop.run_forever()
    log.info('Play server stopped')