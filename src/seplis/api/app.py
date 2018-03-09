import os.path
from tornado import web, httpserver, ioloop
from tornado.web import URLSpec as U
from concurrent.futures import ThreadPoolExecutor
from raven.contrib.tornado import AsyncSentryClient

import seplis
from seplis.api import constants
from seplis.logger import logger
from . import handlers as h

class Application(web.Application):

    def __init__(self, **args):
        settings = dict(
            debug=False,
            autoescape=None,
            xsrf_cookies=False,
        )
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        urls = [
            U(r'/(favicon.ico)', web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            U(r'/static/(.*)', web.StaticFileHandler, {'path': static_path}),

            U(r'/1/shows', h.show.Handler),
            U(r'/1/shows/externals/([a-z_-]+)/([a-z0-9]+)', h.show.External_handler),            
            U(r'/1/shows/([0-9]+)', h.show.Handler),
            U(r'/1/shows/([0-9,]+)', h.show.Multi_handler),
            U(r'/1/shows/([0-9]+)/user-stats', h.user_show_stats.Handler),
            U(r'/1/shows/([0-9]+)/images', h.image.Handler, {'relation_type': 'show'}),
            U(r'/1/shows/([0-9]+)/images/([0-9]+)', h.image.Handler),
            U(r'/1/shows/([0-9]+)/images/([0-9]+)/data', h.image.Data_handler),
            U(r'/1/shows/([0-9]+)/update', h.show.Update_handler),
            U(r'/1/shows/([0-9]+)/episodes', h.episode.Handler),
            U(r'/1/shows/([0-9]+)/episodes/to-watch', h.episode_to_watch.Handler),
            U(r'/1/shows/([0-9]+)/episodes/last-watched', h.episode_last_watched.Handler),
            U(r'/1/shows/([0-9]+)/episodes/([0-9]+)', h.episode.Handler),
            U(r'/1/shows/([0-9]+)/episodes/([0-9]+)/play-servers', h.episode.Play_servers_handler),
            U(r'/1/shows/([0-9]+)/episodes/([0-9]+)/watched', h.episode_watched.Handler),
            U(r'/1/shows/([0-9]+)/episodes/([0-9]+)-([0-9]+)/watched', h.episode_watched.Range_handler),
            U(r'/1/shows/([0-9]+)/episodes/([0-9]+)/position', h.episode_position.Handler),
            
            U(r'/1/users', h.user.Collection_handler),
            U(r'/1/users/current', h.user.Current_handler),            
            U(r'/1/users/current/change-password', h.user.Change_password_handler),
            U(r'/1/users/([0-9]+)', h.user.Handler),        
            U(r'/1/users/([0-9]+)/fan-of', h.user_fan_of.Handler),
            U(r'/1/users/([0-9]+)/fan-of/([0-9]+)', h.user_fan_of.Handler),
            U(r'/1/users/([0-9]+)/show-stats', h.user_shows_stats.Handler),
            U(r'/1/users/([0-9]+)/air-dates', h.air_dates.Handler),
            U(r'/1/users/([0-9]+)/shows-watched', h.shows_watched.Handler,),
            U(r'/1/users/([0-9]+)/shows-recently-aired', h.shows_recently_aired.Handler,),           
            U(r'/1/users/([0-9]+)/shows-countdown', h.shows_countdown.Handler),
            U(r'/1/users/([0-9]+)/shows-etw', h.shows_etw.Handler),        
            U(r'/1/users/([0-9]+)/play-servers/([0-9]+)', h.play.Server_handler),
            U(r'/1/users/([0-9]+)/play-servers', h.play.Server_handler),       
            U(r'/1/users/([0-9]+)/play-servers/([0-9]+)/users', h.play.Access_handler),     
            U(r'/1/users/([0-9]+)/play-servers/([0-9]+)/users/([0-9]+)', h.play.Access_handler),
            U(r'/1/users/([0-9]+)/subtitle-lang/shows/([0-9]+)', h.user_show_subtitle_lang.Handler),

            U(r'/1/apps', h.app.Handler),
            U(r'/1/apps/([0-9]+)', h.app.Handler),
            U(r'/1/token', h.user.Token_handler),
            U(r'/1/progress-token', h.user.Progress_token_handler),
        ]

        self.executor = ThreadPoolExecutor(
            max_workers=seplis.config['api']['max_workers']
        )
        self.ioloop = ioloop.IOLoop.current()
        self.sentry_client = AsyncSentryClient(
            seplis.config['sentry_dsn'],
            raise_send_errors=True
        )
        super().__init__(urls, **settings)

def main():
    logger.set_logger('api-{}.log'.format(seplis.config['api']['port']))

    http_server = httpserver.HTTPServer(Application())
    http_server.listen(seplis.config['api']['port'])

    ioloop.IOLoop.current().start()

if __name__ == '__main__':
    import seplis
    seplis.config_load()
    main()