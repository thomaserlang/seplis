from seplis.config import config
import tornado.web
import tornado.httpserver
import tornado.ioloop
import seplis.web.handlers.react
import seplis.web.handlers.sign_in
import seplis.web.handlers.settings
import seplis.web.handlers.show
import seplis.web.handlers.tag
import seplis.web.handlers.suggest
import seplis.web.handlers.air_dates
import seplis.web.handlers.user.play_servers
import seplis.web.handlers.user.user
import seplis.web.handlers.user.progress_token
import seplis.web.handlers.user.subtitle_lang_show
import seplis.web.handlers.user.change_password
import seplis.web.handlers.play_episode
import seplis.web.handlers.etw
from .handlers.shows import show_episodes
import hashlib
import os, os.path
from seplis.web import modules
from seplis.logger import logger
from seplis import utils
from tornado.options import define, options
from tornado.web import URLSpec

class Application(tornado.web.Application):

    def __init__(self, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=static_path,
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret=config['web']['cookie_secret'],
            login_url='/sign-in',
            ui_modules=dict(
                menu=modules.Menu,
                fan_button=modules.Fan_button,
                watched_button=modules.Watched_button,
                show_header=modules.Show_header,  
                episode_header=modules.Episode_header,
            )
        )

        urls = [
            URLSpec(r'/favicon.ico', tornado.web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            URLSpec(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),

            URLSpec(r"/", tornado.web.RedirectHandler, {"url": "/main"}),
            URLSpec(r"/air-dates", tornado.web.RedirectHandler, {"url": "/main"}),


            URLSpec(r'/show-new', seplis.web.handlers.react.Handler),
            URLSpec(r'/show.*/([0-9]+)', seplis.web.handlers.react.Handler),
            URLSpec(r'/show/([0-9]+)/[^/]+', seplis.web.handlers.react.Handler),
            URLSpec(r'/show-edit/([0-9]+)', seplis.web.handlers.react.Handler),

            URLSpec(r'/fan-of', seplis.web.handlers.react.Handler),
            URLSpec(r'/main', seplis.web.handlers.react.Handler),
            URLSpec(r'/account', seplis.web.handlers.react.Handler),
            URLSpec(r'/password', seplis.web.handlers.react.Handler),
            URLSpec(r'/play-servers', seplis.web.handlers.react.Handler),
            URLSpec(r'/play-server', seplis.web.handlers.react.Handler),

            URLSpec(r'/sign-in', seplis.web.handlers.react.Handler_without_menu),
            URLSpec(r'/create-user', seplis.web.handlers.react.Handler_without_menu),

            URLSpec(r'/show-index', seplis.web.handlers.show.Index_handler),
            URLSpec(r'/show/([0-9]+)/episode/([0-9]+)/play', seplis.web.handlers.play_episode.Handler),

            URLSpec(r'/api/show-new', seplis.web.handlers.show.API_new_handler),
            URLSpec(r'/api/show-edit/([0-9]+)', seplis.web.handlers.show.API_edit_handler),
            URLSpec(r'/api/tvmaze-show-lookup', seplis.web.handlers.show.API_tvmaze_lookup),
            
            URLSpec(r'/api/fan', seplis.web.handlers.show.API_fan_handler),
            URLSpec(r'/api/watched', seplis.web.handlers.show.API_watched_handler),

            URLSpec(r'/api/suggest', seplis.web.handlers.suggest.Handler),

            URLSpec(r'/user-tags', seplis.web.handlers.tag.Relation_handler),
            URLSpec(r'/users/([0-9]+)/tags/shows', seplis.web.handlers.tag.Shows_handler, name='user_tagged_shows'),

            URLSpec(r'/etw', seplis.web.handlers.etw.Handler),

            URLSpec(r'/user/play-servers', seplis.web.handlers.user.play_servers.Handler),
            URLSpec(r'/user/play-server-form', seplis.web.handlers.user.play_servers.Form_handler),
            URLSpec(r'/api/user/play-server', seplis.web.handlers.user.play_servers.API_handler),
            
            URLSpec(r'/api/user/watching', seplis.web.handlers.play_episode.API_watching_handler),

            URLSpec(r'/api/user/default-subtitle-show', seplis.web.handlers.user.subtitle_lang_show.API_handler),
            
            URLSpec(r'/api/show-play-next', seplis.web.handlers.show.API_get_play_now),   
        
            URLSpec(r'/api/users', seplis.web.handlers.user.user.Users_handler),
            
            URLSpec(r'/api/user/play-server/user', seplis.web.handlers.user.play_servers.API_user_handler),
            
            URLSpec(r'/api/progress-token', seplis.web.handlers.user.progress_token.API_handler),
                    
            URLSpec(r'/change-password', seplis.web.handlers.user.change_password.Handler),
            URLSpec(r'/api/change-password', seplis.web.handlers.user.change_password.API_handler),

            URLSpec(r'/api/shows/([0-9]+)/episodes', show_episodes.API_handler)

        ]
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    logger.set_logger('web-{}.log'.format(config['web']['port']))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['web']['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    import seplis
    seplis.config_load()
    main()