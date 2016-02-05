import http
import logging
from tornado import web, gen, ioloop, escape
from seplis import utils, config
from seplis.web.client import API_error, Async_client
from seplis.api import constants

class Handler_unauthenticated(web.RequestHandler):

    @property
    def is_api(self):
        return False

    def initialize(self, *arg, **args):
        super().initialize()
        self.xsrf_token        
        self.client = Async_client(
            url=config['client']['api_url'],
            client_id=config['client']['id'],
        )

    def get_template_namespace(self):
        namespace = web.RequestHandler.get_template_namespace(self)
        namespace.update(
            title='SEPLIS',
            json_dumps=utils.json_dumps,
            escape=self.escape,
            constants=constants,
            config=config,
            image_url=self.image_url,
            plural=self.plural,
            menu_id=None,
        )
        return namespace

    def plural(self, num=0, text=''):
        return '{}{}'.format(
            text, 
            's'[num==1:]
        )

    def escape(self, value):
        if value == None:
            return ''
        return escape.xhtml_escape(value)

    def image_url(self, image, format_=''):
        if not image:
            return ''
        return image['url'] + format_

class Handler(Handler_unauthenticated):

    @gen.coroutine
    def prepare(self):
        access_token = self.get_secure_cookie(
            'session',
            max_age_days=(constants.USER_TOKEN_EXPIRE_DAYS-1),
        )
        if access_token:
            self.client.access_token = access_token.decode('utf-8')
        try:
            self.current_user = self.get_secure_cookie('user')
            self.current_user = utils.json_loads(self.current_user) \
                if self.current_user else None
            if not self.current_user:
                self.current_user = yield self.client.get('/users/current')
                self.current_user = self.current_user.data
                self.set_secure_cookie(
                    'user', 
                    utils.json_dumps(self.current_user),
                    expires_days=None,
                )
            if self.current_user:
                self.current_user = utils.dotdict(self.current_user)
        except API_error as e:
            if e.code == 1009: # not signed in
                if not self.is_api:
                    self.sign_out()
                return
            raise

    def sign_out(self):
        self.clear_cookie('session')
        self.clear_cookie('user')
        self.redirect('/sign-in')


    def write_error(self, status_code, **kwargs):
        if isinstance(kwargs['exc_info'][1], API_error):
            if kwargs['exc_info'][1].code == 1009:
                self.sign_out()
                return
        super().write_error(status_code, **kwargs)

class API_handler(Handler):
    
    @property
    def is_api(self):
        return True    

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.set_header('Content-Type', 'application/json')

    def write_object(self, d):
        self.write(utils.json_dumps(d))

    def write_error(self, status_code, **kwargs):
        if isinstance(kwargs['exc_info'][1], API_error):
            self.write_object({
                'code': kwargs['exc_info'][1].code,
                'message': kwargs['exc_info'][1].message,
                'errors': kwargs['exc_info'][1].errors,
                'extra':  kwargs['exc_info'][1].extra,
            })
            return
        if hasattr(kwargs['exc_info'][1], 'log_message') and kwargs['exc_info'][1].log_message:
            msg = kwargs['exc_info'][1].log_message
        else:
            msg = http.client.responses[status_code]
        self.write_object({
            'code': None, 
            'message': msg, 
            'errors': None,
            'extra': None,
        })
