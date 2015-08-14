import logging
import time
from tornado import gen
from tornado.concurrent import run_on_executor
from tornado.web import HTTPError
from seplis.api.handlers import base
from seplis.api.connections import database
from seplis.api import exceptions, constants, models
from seplis.api.decorators import authenticated, new_session
from seplis.api import exceptions
from seplis import schemas
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from seplis import utils

class Handler(base.Handler):
    '''
    Handles user stuff...
    '''
    @gen.coroutine
    def post(self, user_id=None):
        if user_id: 
            raise exceptions.Parameter_restricted(
                'user_id must not be set.'
            )
        user = yield self.create()
        self.set_status(201)
        self.write_object(user)

    @run_on_executor
    def create(self):
        user = self.validate(schemas.User_schema)
        with new_session() as session:
            user = models.User(
                name=user['name'],
                email=user['email'],
                password=pbkdf2_sha256.encrypt(user['password']),
            )
            session.add(user)
            session.commit()
            return user.serialize()

    @authenticated(0)
    def get(self, user_id=None):
        if not user_id:
            user_id = self.current_user.id
        user = models.User.get(user_id)
        if not user:
            raise exceptions.Not_found('the user was not found')
        self.write_object(self.user_wrapper(user))

class Users_handler(base.Handler):

    def get(self):
        pass

class Stats_handler(base.Handler):

    def get(self, user_id):
        s = {key: 0 for key in constants.USER_STAT_FIELDS}
        stats = database.redis.hgetall('users:{}:stats'.format(user_id))
        for key in stats:
            s[key] = int(stats[key])
        self.write_object(s)

class Token_handler(base.Handler):

    @gen.coroutine
    def post(self):
        data = self.validate(schemas.Token)
        token = None
        if data['grant_type'] == 'password':
            token = yield self.grant_type_password()
        if not token:
            raise exceptions.OAuth_unsuported_grant_type_exception(
                data['grant_type']
            )
        self.write_object({'access_token': token})

    @run_on_executor
    def grant_type_password(self):
        data = self.validate(schemas.Token_type_password)
        app = models.App.by_client_id(data['client_id'])
        if not app:
            raise exceptions.OAuth_unknown_client_id_exception(
                data['client_id']
            )
        if app['level'] != constants.LEVEL_GOD:
            raise exceptions.OAuth_unauthorized_grant_type_level_request_exception(
                constants.LEVEL_GOD, app['level']
            )
        user = models.User.login(
            email_or_username=data['email'],
            password=data['password'],
        )
        if not user:
            raise exceptions.Wrong_email_or_password_exception()
        with new_session() as session:
            token = models.Token(
                app_id=app['id'],
                user_level=user['level'],
                user_id=user['id'],
            )
            session.add(token)
            session.commit()
            return token.token
