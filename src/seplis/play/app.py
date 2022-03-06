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
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=False,
        )
        self.ioloop = ioloop or asyncio.get_event_loop()
        urls = [
            (r'/play', play.Play_handler),            
            (r'/metadata', play.Metadata_handler),
            (r'/hls/(.*)', play.File_handler, {'path': config['play']['temp_folder']}),

            (r'/', shows.Handler),
            (r'/api/show-suggest', shows.API_show_suggest_handler),
            (r'/health', health.Handler),
        ]
        super().__init__(urls, **settings)

def main():
    logger.set_logger('play_server-{}.log'.format(config['play']['port']))
    loop = asyncio.get_event_loop()
    app = Application(loop)
    server = app.listen(config['play']['port'])

    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))
    
    log = logging.getLogger('main')
    log.setLevel('INFO')
    log.info(f'Play server started on port: {config["play"]["port"]}')
    loop.run_forever()
    log.info('Play server stopped')