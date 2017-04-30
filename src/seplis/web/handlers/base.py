import http
import logging
from tornado import web
from seplis import utils, config
from seplis.api import constants

class Handler_unauthenticated(web.RequestHandler):

    @property
    def is_api(self):
        return False

    def initialize(self, *arg, **args):
        super().initialize()
    def get_template_namespace(self):
        namespace = web.RequestHandler.get_template_namespace(self)
        namespace.update(
            title='SEPLIS',
            config=config,
        )
        return namespace

class API_handler(Handler_unauthenticated):
    
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
