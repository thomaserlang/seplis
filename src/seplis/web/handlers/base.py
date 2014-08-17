import http
import logging
from seplis import utils
from seplis.web.client import Api_error
from tornado import web, gen, ioloop

class Handler(web.RequestHandler):

    access_token = None

    def get_template_namespace(self):
        namespace = web.RequestHandler.get_template_namespace(self)
        namespace.update(
            title='SEPLIS',
            json_dumps=utils.json_dumps,
        )
        return namespace

    @property
    def client(self):
        self.application.client.access_token = self.access_token
        return self.application.client

    def write_object(self, d):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(utils.json_dumps(d))
    
    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            if isinstance(kwargs['exc_info'][1], Api_error):
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

class Handler_authenticated(Handler):
    
    @gen.coroutine
    def prepare(self):
        self.access_token = self.get_secure_cookie('session')
        if self.access_token:
            self.access_token = self.access_token.decode('utf-8')
        try:
            self.current_user = yield self.client.get('/users/current')
        except Api_error as e:
            if e.code != 1009: # not signed in
                raise