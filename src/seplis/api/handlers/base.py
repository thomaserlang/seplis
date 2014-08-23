import tornado.web
import tornado.escape
import json
import http.client
import sys
import logging
import redis
from urllib.parse import urljoin
from datetime import datetime
from seplis import utils
from seplis.api import models
from seplis.decorators import new_session
from seplis.api import exceptions
from voluptuous import MultipleInvalid
from seplis.api.base.user import User
from sqlalchemy import or_
from seplis.connections import database
from seplis.api.decorators import authenticated
from seplis.config import config
from seplis import schemas

class Handler(tornado.web.RequestHandler):

    def initialize(self):
        if self.request.body:
            try:
                self.request.body = utils.json_loads(self.request.body)
            except ValueError:
                self.request.body = {}
        else:
            self.request.body = {}

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since, X-Requested-With')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE')
        self.set_header('Access-Control-Expose-Headers', 'ETag, Link, X-Total-Count, X-Total-Pages')
        self.set_header('Access-Control-Max-Age', '86400')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def write_error(self, status_code, **kwargs):
        logging.info('sup')
        if 'exc_info' in kwargs:
            if isinstance(kwargs['exc_info'][1], exceptions.API_exception):
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

    def write_object(self, obj):
        self.write(
            utils.json_dumps(obj, indent=4),
        )

    def write_pagination(self, pagination):
        links = pagination.links_header_format(
            urljoin(config['api']['url'], self.request.path), 
            self.request.query_arguments,
        )
        if links:
            self.set_header('Link', links)
        self.set_header('X-Total-Count', pagination.total)
        self.set_header('X-Total-Pages', pagination.pages)
        self.write_object(pagination.records)

    @property
    def executor(self):
        return self.application.executor

    @property
    def redis(self):
        return database.redis

    @property
    def es(self):
        return database.es

    def get_current_user(self):
        auth = self.request.headers.get('Authorization', None)
        if not auth:
            return None
        bearer = auth.split(' ')
        if len(bearer) != 2:
            return None
        if bearer[0] != 'Bearer':
            raise tornado.web.HTTPError(400, 'Unrecognized token type')
        return User.get_from_token(bearer[1])

    def validate(self, schema, *arg, **args):
        try:
            if not isinstance(schema, schemas.Schema):            
                schema = schemas.Schema(schema, *arg, **args)    
            schema(self.request.body)            
        except MultipleInvalid as e:
            data = []
            for error in e.errors:
                path = '.'.join(str(x) for x in error.path)
                data.append({
                    'field': path,
                    'message': error.msg,
                })
            raise exceptions.Validation_exception(errors=data)

    def options(self, *args, **kwargs):
        pass

    @authenticated(3)
    def check_edit_another_user_right(self):
        pass