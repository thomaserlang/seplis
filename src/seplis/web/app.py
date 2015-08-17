from seplis.config import config
import tornado.web
import tornado.httpserver
import tornado.ioloop
import seplis.web.handlers.sign_in
import seplis.web.handlers.settings
import seplis.web.handlers.show
import seplis.web.handlers.tag
import seplis.web.handlers.suggest
import seplis.web.handlers.air_dates
import seplis.web.handlers.user.play_servers
import seplis.web.handlers.user.user
import seplis.web.handlers.play_episode
import hashlib
import os, os.path
from seplis.web import modules
from seplis.logger import logger
from seplis import utils
from tornado.options import define, options
from tornado.web import URLSpec

def get_static_files(static_path, ext, skip):
    _files = utils.get_files(
        static_path,
        ext,
        skip=skip,
    )
    files = []
    for file_ in _files:
        files.append(
            '/static'+file_[len(static_path):]
        )
    return files

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
        if config['debug']:
            settings['js_files'] = sorted(get_static_files(
                static_path,
                '.js',
                skip=(
                    'seplis.min.js', 
                    'vendor.min.js',
                    'jquery-2.1.3.js',
                    'api.js',
                ),
            ), reverse=True)
            settings['js_files'].insert(0, '/static/js/vendor/jquery-2.1.3.js')
            settings['js_files'].insert(1, '/static/js/api.js')
            settings['css_files'] = sorted(get_static_files(
                static_path,
                '.css',
                skip=(
                    'seplis.min.css', 
                    'vendor.min.css',
                ),
            ), reverse=True)
        else:
            settings['js_files'] = []
            with open(os.path.join(static_path, 'js/vendor/vendor.min.js')) as f:
                settings['js_files'].append(
                    '/static/js/vendor/vendor.min.js?{}'.format(
                        hashlib.md5(f.read().encode('utf-8')).hexdigest()
                    )
                )
            with open(os.path.join(static_path, 'js/seplis.min.js')) as f:
                settings['js_files'].append(
                    '/static/js/seplis.min.js?{}'.format(
                        hashlib.md5(f.read().encode('utf-8')).hexdigest()
                    )
                )
            settings['css_files'] = []
            with open(os.path.join(static_path, 'css/vendor/vendor.min.css')) as f:
                settings['css_files'].append(
                    '/static/css/vendor/vendor.min.css?{}'.format(
                        hashlib.md5(f.read().encode('utf-8')).hexdigest()
                    )
                )
            with open(os.path.join(static_path, 'css/seplis.min.css')) as f:
                settings['css_files'].append(
                    '/static/css/seplis.min.css?{}'.format(
                        hashlib.md5(f.read().encode('utf-8')).hexdigest()
                    )
                )

        urls = [
            URLSpec(r'/favicon.ico', tornado.web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            URLSpec(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),

            URLSpec(r"/", tornado.web.RedirectHandler, {"url": "/air-dates"}),

            URLSpec(r'/sign-in', seplis.web.handlers.sign_in.Handler),
            URLSpec(r'/api/sign-in', seplis.web.handlers.sign_in.API_handler),
            URLSpec(r'/sign-up', seplis.web.handlers.sign_in.Sign_up_handler),
            URLSpec(r'/api/sign-up', seplis.web.handlers.sign_in.API_sign_up_handler),
            URLSpec(r'/settings', seplis.web.handlers.settings.Handler),
            URLSpec(r'/sign-out', seplis.web.handlers.sign_in.Sign_out_handler),

            URLSpec(r'/show-index', seplis.web.handlers.show.Index_handler),
            URLSpec(r'/show/([0-9]+)', seplis.web.handlers.show.Redirect_handler),
            URLSpec(r'/show/([0-9]+)/[^/]+', seplis.web.handlers.show.Handler),
            URLSpec(r'/show/([0-9]+)/episode/([0-9]+)/play', seplis.web.handlers.play_episode.Handler),

            URLSpec(r'/show-new', seplis.web.handlers.show.New_handler),
            URLSpec(r'/api/show-new', seplis.web.handlers.show.API_new_handler),
            URLSpec(r'/show-edit/([0-9]+)', seplis.web.handlers.show.Edit_handler),
            URLSpec(r'/api/show-edit/([0-9]+)', seplis.web.handlers.show.API_edit_handler),

            URLSpec(r'/api/fan', seplis.web.handlers.show.API_fan_handler),
            URLSpec(r'/api/watched', seplis.web.handlers.show.API_watched_handler),

            URLSpec(r'/api/suggest', seplis.web.handlers.suggest.Handler),

            URLSpec(r'/user-tags', seplis.web.handlers.tag.Relation_handler),
            URLSpec(r'/users/([0-9]+)/tags/shows', seplis.web.handlers.tag.Shows_handler, name='user_tagged_shows'),

            URLSpec(r'/air-dates', seplis.web.handlers.air_dates.Handler),
            URLSpec(r'/fan-of', seplis.web.handlers.show.Fan_of_handler),

            URLSpec(r'/user/play-servers', seplis.web.handlers.user.play_servers.Handler),
            URLSpec(r'/user/play-server-form', seplis.web.handlers.user.play_servers.Form_handler),
            URLSpec(r'/api/user/play-server', seplis.web.handlers.user.play_servers.API_handler),
            
            URLSpec(r'/api/user/watching', seplis.web.handlers.play_episode.API_watching_handler),
            
            URLSpec(r'/api/show-play-next', seplis.web.handlers.show.API_get_play_now),   
        
            URLSpec(r'/api/users', seplis.web.handlers.user.user.Users_handler),
            
            URLSpec(r'/api/user/play-server/user', seplis.web.handlers.user.play_servers.API_user_handler),
            
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