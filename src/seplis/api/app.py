from seplis.config import config
import tornado.web
import tornado.httpserver
import tornado.ioloop
import seplis.api.handlers.base
import seplis.api.handlers.show
import seplis.api.handlers.user
import seplis.api.handlers.app
import seplis.api.handlers.tag
import seplis.api.handlers.episode
from seplis.logger import logger
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor

class Application(tornado.web.Application):

    def __init__(self, **args):
        settings = dict(
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=False,
        )

        urls = [
            (r'/1/shows', seplis.api.handlers.show.Handler),
            (r'/1/shows/externals/([a-z_-]+)/([a-z0-9]+)', seplis.api.handlers.show.External_handler),
            (r'/1/shows/([0-9]+)', seplis.api.handlers.show.Handler),
            (r'/1/shows/([0-9,]+)', seplis.api.handlers.show.Multi_handler),
            (r'/1/shows/([0-9]+)/episodes', seplis.api.handlers.episode.Handler),
            (r'/1/shows/([0-9]+)/episodes/([0-9]+)', seplis.api.handlers.episode.Handler),
            (r'/1/shows/([0-9]+)/follow', seplis.api.handlers.show.Follow_handler),

            (r'/1/suggest-shows', seplis.api.handlers.show.Suggest_handler),

            (r'/1/users', seplis.api.handlers.user.Handler),
            (r'/1/users/current', seplis.api.handlers.user.Handler),
            (r'/1/users/([0-9]+)', seplis.api.handlers.user.Handler),
            
            (r'/1/users/([0-9]+)/follows', seplis.api.handlers.show.Follows_handler),
            (r'/1/users/([0-9]+)/watched/shows/([0-9]+)/episodes/([0-9]+)', seplis.api.handlers.episode.Watched_handler),

            (r'/1/users/([0-9]+)/tags', seplis.api.handlers.tag.User_types_handler),
            (r'/1/users/([0-9]+)/tags/shows/([0-9]+)', seplis.api.handlers.tag.Relation_handler, {'type_': 'shows'}),
            (r'/1/users/([0-9]+)/tags/([0-9]+)/shows/([0-9]+)', seplis.api.handlers.tag.Relation_handler, {'type_': 'shows'}),
            (r'/1/users/([0-9]+)/tags/shows', seplis.api.handlers.tag.Relations_handler, {'type_': 'shows'}),
            (r'/1/users/([0-9]+)/tags/([0-9]+)/shows', seplis.api.handlers.tag.Relations_handler, {'type_': 'shows'}),

            (r'/1/apps', seplis.api.handlers.app.Handler),
            (r'/1/apps/([0-9]+)', seplis.api.handlers.app.Handler),
            (r'/1/token', seplis.api.handlers.user.Token_handler),

            (r'.*', seplis.api.handlers.base.Handler),      
        ]

        self.executor = ThreadPoolExecutor(
            max_workers=config['api']['max_workers']
        )
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    logger.set_logger('api-{}.log'.format(config['api']['port']))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['api']['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    import seplis.config
    seplis.config.load()
    main()