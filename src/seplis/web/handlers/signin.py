import logging
from seplis.web.handlers import base
from tornado import gen
from seplis import utils

class Handler(base.Handler):
    
    def get(self):
        self.render(
            'signin.html', 
            title='Sign in - SEPLIS',
        )

class API_handler(base.API_handler):
    
    @gen.coroutine
    def post(self):
        response = yield self.client.post('/token', {
            'client_id': self.client.client_id,
            'grant_type': 'password',
            'email': self.get_argument('email'),
            'password': self.get_argument('password'),
        })
        self.set_secure_cookie(
            name='session',
            value=response['access_token'],
            expires_days=365 if self.get_argument('remember_me', 'false') == 'true' else None,
        )
        self.write_object({})