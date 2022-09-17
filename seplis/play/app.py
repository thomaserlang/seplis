import asyncio
from functools import partial
import logging
import signal
from seplis.io_sighandler import sig_handler
from seplis.play.handlers import play, health
import tornado.web
from seplis import config

class Application(tornado.web.Application):

    def __init__(self, **args):
        settings = dict(
            debug=config.data.debug,
            autoescape=None,
            xsrf_cookies=False,
        )
        urls = [
            (r'/transcode', play.Transcode_handler),
            (r'/subtitle-file', play.Subtitle_file_handler),
            (r'/sources', play.Sources_handler),
            (r'/files/(.*)/transcode', play.Transcode_handler),
            (r'/files/(.*)', play.File_handler),
            (r'/thumbnails/(.*)', play.Thumbnails_handler),
            (r'/close-session/(.*)', play.Close_session_handler),
            (r'/keep-alive/(.*)', play.Keep_alive_handler),
            (r'/health', health.Handler),
        ]
        super().__init__(urls, **settings)

async def main():
    app = Application()
    server = app.listen(config.data.play.port)

    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))
    
    logging.getLogger('tornado.access').setLevel(config.data.logging.level.upper())
    log = logging.getLogger('main')
    log.setLevel('INFO')
    log.info(f'Play server started on port: {config.data.play.port}')
    await asyncio.Event().wait()
    log.info('Play server stopped')