import seplis.play.handlers.play
import seplis.play.handlers.play2
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
            (r'/(.*)/media/(.*)', seplis.play.handlers.play.Hls_file_handler),
            (r'/(.*)/cancel', seplis.play.handlers.play.Hls_cancel_handler),
            (r'/(.*)/ping', seplis.play.handlers.play.Hls_ping_handler),
            (r'/hls/(.*)', seplis.play.handlers.play2.File_handler, {'path': config['play']['temp_folder']}),
            
            (r'/transcode', seplis.play.handlers.play.Transcode_handler),
            (r'/play', seplis.play.handlers.play.Play_handler),
            (r'/play2', seplis.play.handlers.play2.Play_handler),
            
            (r'/', seplis.play.handlers.play.Play_shows_handler),

            (r'/metadata', seplis.play.handlers.play.Metadata_handler),


            (r'/api/show-suggest', seplis.play.handlers.play.API_show_suggest_handler),
        ]
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['play']['port'])
    tornado.ioloop.IOLoop.instance().start()