import logging
import time, re, good
from sqlalchemy import or_
from tornado import gen
from tornado.web import HTTPError
from seplis.api.handlers import base
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from seplis.api import exceptions, constants, models
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import exceptions
from seplis import schemas
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timedelta
from seplis import utils

class Handler(base.Handler):

    __schema__ = good.Schema({
        'name': good.All(
            str, 
            good.Length(min=1, max=45), 
            good.Match(re.compile(r'^[a-z0-9-_]+$', re.I),
            message='must only contain a-z, 0-9, _ and -')
        ),    
        'email': good.All(str, good.Length(min=1, max=100), schemas.validate_email),
        'password': good.All(str, good.Length(min=6)),
    })

    async def get(self, user_id=None):
        if not user_id:
            users = await self.get_users()
            self.write_object(users)
        else:
            user = models.User.get(user_id)
            if not user:
                raise exceptions.Not_found('the user was not found')
            self.write_object(self.user_wrapper(user))

    async def post(self, user_id=None):
        if user_id: 
            raise exceptions.Parameter_restricted(
                'user_id must not be set.'
            )
        user = await self.create()
        self.set_status(201)
        self.write_object(user)

    @run_on_executor
    def create(self):
        user = self.validate()
        with new_session() as session:
            u = session.query(models.User.id).filter(
                models.User.email == user['email']
            ).first()
            if u:
                raise exceptions.User_email_duplicate()

            u = session.query(models.User.id).filter(
                models.User.name == user['name']
            ).first()
            if u:
                raise exceptions.User_username_duplicate()

            user = models.User(
                name=user['name'],
                email=user['email'],
                password=pbkdf2_sha256.encrypt(user['password']),
            )
            session.add(user)
            session.commit()
            return user.serialize()

    @run_on_executor
    def get_users(self):
        username = self.get_argument('username')
        with new_session() as session:
            user = session.query(models.User).filter(
                models.User.name == username,
            ).first()
            if user:
                return [self.user_wrapper(user.serialize())]
            return []

class Current_handler(Handler):

    @authenticated(0)
    async def get(self):
        await super().get(self.current_user.id)

    def post(self):
        raise HTTPError(405)

    def put(self):
        raise HTTPError(405)

    def delete(self):
        raise HTTPError(405) 

class Token_handler(base.Handler):

    async def post(self):
        data = self.validate(schemas.Token)
        token = None
        if data['grant_type'] == 'password':
            token = await self.grant_type_password()
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

class Progress_token_handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    async def get(self):
        token = await self.get_token()
        self.write_object({
            'token': token,
        })

    @run_on_executor
    def get_token(self):
        with new_session() as session:
            token = models.Token(
                app_id=None,
                user_id=self.current_user.id,
                user_level=constants.LEVEL_PROGRESS,
                expires=datetime.utcnow()+timedelta(days=1),
            )
            session.add(token)
            session.commit()
            return token.token

class Change_password_handler(base.Handler):

    __schema__ = good.Schema({
        'password': str,
        'new_password': good.All(str, good.Length(min=6)),
    })

    @authenticated(constants.LEVEL_USER)
    async def post(self, user_id=None):
        user_id = user_id if user_id else self.current_user.id
        self.check_user_edit(user_id)
        await self.change_password(user_id)
        self.set_status(204)

    @run_on_executor
    def change_password(self, user_id):
        data = self.validate()        
        if not models.User.login(int(user_id), data['password']):
            raise exceptions.Wrong_email_or_password_exception()
        with new_session() as session:
            models.User.change_password(
                user_id=user_id,
                new_password=data['new_password'],
                session=session,
            )
            tokens = session.query(models.Token).filter(
                models.Token.user_id == user_id,
                or_(
                    models.Token.expires >= datetime.utcnow(),
                    models.Token.expires == None,
                )
            ).all()
            for token in tokens:
                if token.token == self.access_token:
                    continue
                session.delete(token)
            session.commit()