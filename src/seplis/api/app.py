from functools import partial
import os.path, asyncio, logging
import signal
from tornado import web
from tornado.web import URLSpec as U
from concurrent.futures import ThreadPoolExecutor
import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration

import seplis
from seplis.logger import logger
from seplis.io_sighandler import sig_handler
from . import handlers as h

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
    U(r'/1/shows/([0-9]+)/user-subtitle-lang', h.user_show_subtitle_lang.Handler),
    U(r'/1/shows/([0-9]+)/episodes', h.episode.Handler),
    U(r'/1/shows/([0-9]+)/episodes/to-watch', h.episode_to_watch.Handler),
    U(r'/1/shows/([0-9]+)/episodes/last-watched', h.episode_last_watched.Handler),
    U(r'/1/shows/([0-9]+)/episodes/([0-9]+)', h.episode.Handler),
    U(r'/1/shows/([0-9]+)/episodes/([0-9]+)/play-servers', h.episode.Play_servers_handler),
    U(r'/1/shows/([0-9]+)/episodes/([0-9]+)/watched', h.episode_watched.Handler),
    U(r'/1/shows/([0-9]+)/episodes/([0-9]+)-([0-9]+)/watched', h.episode_watched.Range_handler),
    U(r'/1/shows/([0-9]+)/episodes/([0-9]+)/position', h.episode_position.Handler),
    U(r'/1/shows/([0-9]+)/user-rating', h.user_show_rating.Handler),
    
    U(r'/1/movies', h.movie.Handler),
    U(r'/1/movies/([0-9]+)', h.movie.Handler),
    U(r'/1/movies/([0-9]+)/update', h.movie.Update_handler),    
    U(r'/1/movies/([0-9]+)/watched', h.movie_watched.Handler),
    U(r'/1/movies/([0-9]+)/position', h.movie_position.Handler),
    U(r'/1/movies/([0-9]+)/stared', h.movie_stared.Handler),
    U(r'/1/movies/([0-9]+)/images', h.image.Handler, {'relation_type': 'movie'}),
    U(r'/1/movies/([0-9]+)/images/([0-9]+)', h.image.Handler),
    U(r'/1/movies/([0-9]+)/images/([0-9]+)/data', h.image.Data_handler),
    U(r'/1/movies/([0-9]+)/play-servers', h.movie.Play_servers_handler),
    U(r'/1/movies/externals/([a-z_-]+)/([a-z0-9]+)', h.movie_external.Handler),

    U(r'/1/search', h.search.Handler),

    U(r'/1/users', h.user.Collection_handler),
    U(r'/1/users/current', h.user.Current_handler),            
    U(r'/1/users/current/change-password', h.user.Change_password_handler),
    U(r'/1/user-reset-password', h.reset_password.Handler),
    U(r'/1/users/([a-z0-9]+)', h.user.Handler),
    U(r'/1/users/([a-z0-9]+)/fan-of', h.shows_following.Handler),
    U(r'/1/users/([a-z0-9]+)/fan-of/([0-9]+)', h.shows_following.Handler),
    U(r'/1/users/([a-z0-9]+)/shows-following', h.shows_following.Handler),
    U(r'/1/users/([a-z0-9]+)/shows-following/([0-9]+)', h.shows_following.Handler),
    U(r'/1/users/([a-z0-9]+)/show-stats', h.user_shows_stats.Handler),
    U(r'/1/users/([a-z0-9]+)/air-dates', h.air_dates.Handler),
    U(r'/1/users/([a-z0-9]+)/shows-watched', h.shows_watched.Handler,),
    U(r'/1/users/([a-z0-9]+)/shows-recently-aired', h.shows_recently_aired.Handler),
    U(r'/1/users/([a-z0-9]+)/shows-countdown', h.shows_countdown.Handler),
    U(r'/1/users/([a-z0-9]+)/shows-etw', h.shows_etw.Handler),
    U(r'/1/users/me/movies-stared', h.movies_stared.Handler),
    U(r'/1/users/me/movies-watched', h.movies_watched.Handler),
        

    U(r'/1/play-servers', h.play_server.Collection_handler),
    U(r'/1/play-servers/([0-9]+)', h.play_server.Handler),
    U(r'/1/play-servers/([0-9]+)/users', h.play_server.Access_handler),
    U(r'/1/play-servers/([0-9]+)/users/([0-9]+)', h.play_server.Access_handler),

    U(r'/1/apps', h.app.Handler),
    U(r'/1/apps/([0-9]+)', h.app.Handler),
    U(r'/1/token', h.user.Token_handler),
    U(r'/1/progress-token', h.user.Progress_token_handler),

    U(r'/1/show-genres', h.genres.Handler),
    U(r'/health', h.health.Handler),
]

class Application(web.Application):

    def __init__(self, ioloop=None, **args):
        settings = dict(
            debug=seplis.config['debug'],
            autoescape=None,
            xsrf_cookies=False,
        )
        self.ioloop = ioloop or asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(
            max_workers=seplis.config['api']['max_workers']
        )
        super().__init__(urls, **settings)

async def main():
    logger.set_logger('api-{}.log'.format(seplis.config['api']['port']))
    if seplis.config['sentry_dsn']:
        sentry_sdk.init(
            dsn=seplis.config['sentry_dsn'],
            integrations=[TornadoIntegration()],
        )
    loop = asyncio.get_event_loop()
    app = Application(loop)
    server = app.listen(seplis.config['api']['port'])

    signal.signal(signal.SIGTERM, partial(sig_handler, server, app))
    signal.signal(signal.SIGINT, partial(sig_handler, server, app))

    log = logging.getLogger('main')
    log.setLevel('INFO')
    log.info(f'API server started on port: {seplis.config["api"]["port"]}')
    await asyncio.Event().wait()
    log.info('API server stopped')
