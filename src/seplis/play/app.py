import seplis.play.handlers.play
import seplis.play.handlers.shows
import tornado.web
import tornado.ioloop
import tornado.httpserver
import os, os.path
from seplis import config

class Application(tornado.web.Application):

    def __init__(self, **args):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=seplis.config['debug'],
            autoescape=None,
            xsrf_cookies=False,
        )
        urls = [
            (r'/play', seplis.play.handlers.play.Play_handler),            
            (r'/metadata', seplis.play.handlers.play.Metadata_handler),
            (r'/hls/(.*)', seplis.play.handlers.play.File_handler, {'path': config['play']['temp_folder']}),

            (r'/', seplis.play.handlers.shows.Handler),
            (r'/api/show-suggest', seplis.play.handlers.shows.API_show_suggest_handler),
        ]
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['play']['port'])
    tornado.ioloop.IOLoop.instance().start()