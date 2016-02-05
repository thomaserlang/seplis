import logging
from seplis.web.handlers import base
from tornado import gen
from tornado.web import authenticated
from seplis import utils

class Handler(base.Handler):
    
    def get(self):
        self.render(
            'sign_in.html', 
            title='Sign in',
        )

    def post(self):
        get()

class API_handler(base.API_handler):
    
    @gen.coroutine
    def post(self):
        yield self.sign_in()
        self.write_object({})

    @gen.coroutine
    def sign_in(self):
        response = yield self.client.post('/token', {
            'client_id': self.client.client_id,
            'grant_type': 'password',
            'email': self.get_argument('email'),
            'password': self.get_argument('password'),
        })
        self.set_secure_cookie(
            name='session',
            value=response['access_token'],
            expires_days=constants.USER_TOKEN_EXPIRE_DAYS \
                if self.get_argument('remember_me', 'true') == 'true' \
                    else None,
        )

class Sign_up_handler(base.Handler):

    def get(self):
        self.render('sign_up.html')

class API_sign_up_handler(API_handler):

    @gen.coroutine
    def post(self):
        response = yield self.client.post('users', {
            'name': self.get_argument('username'),
            'email': self.get_argument('email'),
            'password': self.get_argument('password'),
        })
        yield self.sign_in()
        self.write_object(response.data)

class Sign_out_handler(base.Handler):

    @authenticated
    def get(self):
        self.clear_cookie('session')
        self.clear_cookie('user')
        self.redirect('/')