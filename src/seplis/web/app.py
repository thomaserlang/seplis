from seplis.config import config
import tornado.web
import tornado.httpserver
import tornado.ioloop
import seplis.web.handlers.signin
import seplis.web.handlers.settings
import seplis.web.handlers.show
import seplis.web.handlers.tag
import seplis.web.handlers.suggest
import seplis.web.handlers.air_dates
import seplis.web.modules.menu
import seplis.web.modules.buttons
import seplis.web.modules.tags
import os
from seplis.logger import logger
from tornado.options import define, options

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
            login_url='/signin',
            ui_modules=dict(
                menu=seplis.web.modules.menu.Module,
                fan_button=seplis.web.modules.buttons.Fan_module,
                watched_button=seplis.web.modules.buttons.Watched_module,
                tags=seplis.web.modules.tags.Module,
            )
        )
        urls = [
            tornado.web.URLSpec(r'/favicon.ico', tornado.web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            tornado.web.URLSpec(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),

            # (r'/signup', handlers.signup.Handler),
            tornado.web.URLSpec(r'/signin', seplis.web.handlers.signin.Handler),
            tornado.web.URLSpec(r'/api/signin', seplis.web.handlers.signin.API_handler),
            tornado.web.URLSpec(r'/settings', seplis.web.handlers.settings.Handler),

            tornado.web.URLSpec(r'/show/([0-9]+)', seplis.web.handlers.show.Redirect_handler),
            tornado.web.URLSpec(r'/show/([0-9]+)/[^/]+', seplis.web.handlers.show.Handler),
            tornado.web.URLSpec(r'/show-new', seplis.web.handlers.show.New_handler),
            tornado.web.URLSpec(r'/api/show-new', seplis.web.handlers.show.API_new_handler),
            tornado.web.URLSpec(r'/show-edit/([0-9]+)', seplis.web.handlers.show.Edit_handler),
            tornado.web.URLSpec(r'/api/show-edit/([0-9]+)', seplis.web.handlers.show.API_edit_handler),

            tornado.web.URLSpec(r'/api/fan', seplis.web.handlers.show.API_fan_handler),
            tornado.web.URLSpec(r'/api/watched', seplis.web.handlers.show.API_watched_handler),

            tornado.web.URLSpec(r'/api/suggest', seplis.web.handlers.suggest.Handler),

            tornado.web.URLSpec(r'/user-tags', seplis.web.handlers.tag.Relation_handler),
            tornado.web.URLSpec(r'/users/([0-9]+)/tags/shows', seplis.web.handlers.tag.Shows_handler, name='user_tagged_shows'),

            tornado.web.URLSpec(r'/air-dates', seplis.web.handlers.air_dates.Handler),
            tornado.web.URLSpec(r'/fan-of', seplis.web.handlers.show.Fan_of_handler),

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