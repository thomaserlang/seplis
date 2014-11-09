import tornado.web
import tornado.gen
import logging
import time
from tornado.concurrent import run_on_executor
from tornado.web import HTTPError
from seplis.api.handlers import base
from seplis.api.connections import database
from seplis.api import models
from seplis.api.base.user import User, Token
from seplis.api.base.app import App
from seplis.api import exceptions
from seplis import schemas
from passlib.hash import pbkdf2_sha256
from seplis.api import exceptions
from datetime import datetime
from seplis.api import constants
from seplis.api.decorators import authenticated
from seplis import utils

class Handler(base.Handler):
    '''
    Handles user stuff...
    '''
    @tornado.gen.coroutine
    def post(self, user_id=None):
        if user_id: 
            raise exceptions.Parameter_must_not_be_set_exception(
                'user_id must not be set.'
            )
        self.validate(schemas.User_schema)
        password = yield self.encrypt_password(self.request.body['password'])
        user = User.new(
            name=self.request.body['name'],   
            email=self.request.body['email'],
            password=password,
        ).to_dict(user_level=constants.LEVEL_SHOW_USER_EMAIL)
        self.set_status(201)
        self.write_object(user)

    @run_on_executor
    def encrypt_password(self, password):
        return pbkdf2_sha256.encrypt(password)

    @authenticated(0)
    def get(self, user_id=None):
        if not user_id:
            user_id = self.current_user.id
        user = User.get(user_id)
        if not user:
            raise exceptions.Not_found('the user was not found')
        user = user.to_dict(
            user_level=user.level if self.current_user.id != user_id else \
                constants.LEVEL_SHOW_USER_EMAIL,
        )
        self.write_object(user)

class Stats_handler(base.Handler):

    def get(self, user_id):
        s = {key: 0 for key in constants.USER_STAT_FIELDS}
        stats = database.redis.hgetall('users:{}:stats'.format(user_id))
        for key in stats:
            s[key] = int(stats[key])
        self.write_object(s)

class Token_handler(base.Handler):

    @tornado.gen.coroutine
    def post(self):
        self.validate(schemas.Token)
        if self.request.body['grant_type'] == 'password':
            yield self.grant_type_password()
        else:
            raise exceptions.OAuth_unsuported_grant_type_exception(
                self.request.body['grant_type']
            )

    @run_on_executor
    def grant_type_password(self):
        self.validate(schemas.Token_type_password)
        app = App.get_by_client_id(client_id=self.request.body['client_id'])
        if not app:
            raise exceptions.OAuth_unknown_client_id_exception(
                self.request.body['client_id']
            )
        if app.level != constants.LEVEL_GOD:
            raise exceptions.OAuth_unauthorized_grant_type_level_request_exception(
                constants.LEVEL_GOD, app.level
            )
        user = User.login(
            email=self.request.body['email'],
            password=self.request.body['password'],
        )
        if not user:
            raise exceptions.Wrong_email_or_password_exception()
        self.write_object({'access_token': Token.new(
            user_id=user.id,
            user_level=user.level,
            app_id=app.id,
        )})