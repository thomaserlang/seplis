import os.path
import seplis
import asyncio
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.platform.asyncio
import seplis.api.handlers.base
import seplis.api.handlers.show
import seplis.api.handlers.user
import seplis.api.handlers.app
import seplis.api.handlers.episode
import seplis.api.handlers.image
import seplis.api.handlers.play
import seplis.api.handlers.shows_watched
import seplis.api.handlers.air_dates
import seplis.api.handlers.episode_watched
import seplis.api.handlers.episode_position
import seplis.api.handlers.episode_to_watch
import seplis.api.handlers.episode_last_watched
import seplis.api.handlers.user_show_subtitle_lang
import seplis.api.handlers.user_fan_of
import seplis.api.handlers.shows_countdown
import seplis.api.handlers.shows_recently_aired
import seplis.api.handlers.shows_etw
import seplis.api.handlers.user_shows_stats
import seplis.api.handlers.user_show_stats
from seplis.api import constants
from seplis.logger import logger
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor
from raven.contrib.tornado import AsyncSentryClient
from tornado.web import URLSpec

class Application(tornado.web.Application):

    def __init__(self, **args):
        settings = dict(
            debug=False,
            autoescape=None,
            xsrf_cookies=False,
        )
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        urls = [
            URLSpec(
                r'/(favicon.ico)', 
                tornado.web.StaticFileHandler, 
                {'path': os.path.join(static_path, 'favicon.ico')}
            ),
            URLSpec(
                r'/static/(.*)', 
                tornado.web.StaticFileHandler, 
                {'path': static_path}
            ),

            URLSpec(
                r'/1/shows', 
                seplis.api.handlers.show.Handler
            ),
            URLSpec(
                r'/1/shows/externals/([a-z_-]+)/([a-z0-9]+)', 
                seplis.api.handlers.show.External_handler
            ),
            
            URLSpec(
                r'/1/shows/([0-9]+)', 
                seplis.api.handlers.show.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9,]+)', 
                seplis.api.handlers.show.Multi_handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/user-stats', 
                seplis.api.handlers.user_show_stats.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes', 
                seplis.api.handlers.episode.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/([0-9]+)', 
                seplis.api.handlers.episode.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/([0-9]+)/play-servers', 
                seplis.api.handlers.episode.Play_servers_handler
            ),
            

            URLSpec(
                r'/1/shows/([0-9]+)/images', 
                seplis.api.handlers.image.Handler, {'relation_type': 'show'}),
            URLSpec(
                r'/1/shows/([0-9]+)/images/([0-9]+)', 
                seplis.api.handlers.image.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/images/([0-9]+)/data', 
                seplis.api.handlers.image.Data_handler
            ),

            URLSpec(
                r'/1/shows/([0-9]+)/update', 
                seplis.api.handlers.show.Update_handler
            ),

            URLSpec(
                r'/1/users', 
                seplis.api.handlers.user.Handler
            ),
            URLSpec(
                r'/1/users/current', 
                seplis.api.handlers.user.Current_handler
            ),            
            URLSpec(
                r'/1/users/current/change-password', 
                seplis.api.handlers.user.Change_password_handler
            ),
            
            URLSpec(
                r'/1/users/([0-9]+)', 
                seplis.api.handlers.user.Handler
            ),
        
            URLSpec(
                r'/1/users/([0-9]+)/fan-of', 
                seplis.api.handlers.user_fan_of.Handler
            ),
            URLSpec(
                r'/1/users/([0-9]+)/fan-of/([0-9]+)', 
                seplis.api.handlers.user_fan_of.Handler
            ),
            URLSpec(
                r'/1/users/([0-9]+)/show-stats',
                seplis.api.handlers.user_shows_stats.Handler
            ),

            URLSpec(
                r'/1/users/([0-9]+)/air-dates', 
                seplis.api.handlers.air_dates.Handler
            ),

            URLSpec(
                r'/1/users/([0-9]+)/shows-watched', 
                seplis.api.handlers.shows_watched.Handler,
            ),      

            URLSpec(
                r'/1/users/([0-9]+)/shows-recently-aired', 
                seplis.api.handlers.shows_recently_aired.Handler,
            ),           

            URLSpec(
                r'/1/users/([0-9]+)/shows-countdown', 
                seplis.api.handlers.shows_countdown.Handler
            ),
            URLSpec(
                r'/1/users/([0-9]+)/shows-etw', 
                seplis.api.handlers.shows_etw.Handler
            ),
        
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/([0-9]+)/watched', 
                seplis.api.handlers.episode_watched.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/([0-9]+)-([0-9]+)/watched', 
                seplis.api.handlers.episode_watched.Range_handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/([0-9]+)/position', 
                seplis.api.handlers.episode_position.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/to-watch', 
                seplis.api.handlers.episode_to_watch.Handler
            ),
            URLSpec(
                r'/1/shows/([0-9]+)/episodes/last-watched', 
                seplis.api.handlers.episode_last_watched.Handler
            ),

            URLSpec(
                r'/1/users/([0-9]+)/play-servers/([0-9]+)', 
                seplis.api.handlers.play.Server_handler
            ),
            URLSpec(
                r'/1/users/([0-9]+)/play-servers', 
                seplis.api.handlers.play.Server_handler
            ),       
            URLSpec(
                r'/1/users/([0-9]+)/play-servers/([0-9]+)/users', 
                seplis.api.handlers.play.Access_handler
            ),     
            URLSpec(
                r'/1/users/([0-9]+)/play-servers/([0-9]+)/users/([0-9]+)', 
                seplis.api.handlers.play.Access_handler
            ),
           
            URLSpec(
                r'/1/users/([0-9]+)/subtitle-lang/shows/([0-9]+)', 
                seplis.api.handlers.user_show_subtitle_lang.Handler
            ),

            URLSpec(
                r'/1/apps', 
                seplis.api.handlers.app.Handler
            ),
            URLSpec(
                r'/1/apps/([0-9]+)', 
                seplis.api.handlers.app.Handler
            ),
            URLSpec(
                r'/1/token', 
                seplis.api.handlers.user.Token_handler
            ),
            URLSpec(
                r'/1/progress-token', 
                seplis.api.handlers.user.Progress_token_handler
            ),

            URLSpec(
                r'.*', 
                seplis.api.handlers.base.Handler
            ),      
        ]

        self.executor = ThreadPoolExecutor(
            max_workers=seplis.config['api']['max_workers']
        )
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.sentry_client = AsyncSentryClient(
            seplis.config['sentry_dsn'],
            raise_send_errors=True
        )
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    logger.set_logger('api-{}.log'.format(seplis.config['api']['port']))

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(seplis.config['api']['port'])

    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    import seplis
    seplis.config_load()
    main()