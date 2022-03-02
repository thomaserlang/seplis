import asyncio
from functools import partial
import logging
import signal
from seplis.io_sighandler import sig_handler
import seplis.play.handlers.play
import seplis.play.handlers.shows
import tornado.web
import tornado.ioloop
import tornado.httpserver
import os, os.path
from seplis import config, health

class Application(tornado.web.Application):

    def __init__(self, ioloop=None, **args):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=seplis.config['debug'],
            autoescape=None,
            xsrf_cookies=False,
        )
        self.ioloop = ioloop or asyncio.get_event_loop()
        urls = [
            (r'/play', seplis.play.handlers.play.Play_handler),            
            (r'/metadata', seplis.play.handlers.play.Metadata_handler),
            (r'/hls/(.*)', seplis.play.handlers.play.File_handler, {'path': config['play']['temp_folder']}),

            (r'/', seplis.play.handlers.shows.Handler),
            (r'/api/show-suggest', seplis.play.handlers.shows.API_show_suggest_handler),
            (r'/health', health.Handler),
        ]
        super().__init__(urls, **settings)

def main():
    ioloop = asyncio.get_event_loop()
    app = Application(ioloop)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(config['play']['port'])
    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))    
    logging.info(f'Play server started on port: {config["play"]["port"]}')
    ioloop.run_forever()