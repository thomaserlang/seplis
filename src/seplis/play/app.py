import tornado.web
import seplis.play.handlers.play
import tornado.ioloop
from seplis import config

application = tornado.web.Application([
    (r'/(.*)/media/(.*)', seplis.play.handlers.play.Hls_file_handler),
    (r'/(.*)/cancel', seplis.play.handlers.play.Hls_cancel_handler),

    (r'/play', seplis.play.handlers.play.Play_handler),
    (r'/metadata', seplis.play.handlers.play.Metadata_handler),
    
], debug=True)

def main():
    application.listen(config['play']['port'])
    tornado.ioloop.IOLoop.instance().start()