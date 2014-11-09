import tornado.web
import tornado.escape
import json
import http.client
import sys
import logging
import redis
from sqlalchemy import or_
from voluptuous import MultipleInvalid
from tornado import gen
from urllib.parse import urljoin
from datetime import datetime
from raven.contrib.tornado import SentryMixin
from tornado.httpclient import AsyncHTTPClient, HTTPError
from seplis import utils, schemas
from seplis.api.decorators import new_session
from seplis.api.connections import database
from seplis.config import config
from seplis.api import models, exceptions, constants
from seplis.api.base.user import User
from seplis.api.base.pagination import Pagination
from seplis.api.decorators import authenticated

class Handler(tornado.web.RequestHandler, SentryMixin):

    def initialize(self):
        self.access_token = None
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
        if isinstance(kwargs['exc_info'][1], exceptions.API_exception):
            self.write_object({
                'code': kwargs['exc_info'][1].code,
                'message': kwargs['exc_info'][1].message,
                'errors': kwargs['exc_info'][1].errors,
                'extra':  kwargs['exc_info'][1].extra,
            })
            return 
        elif isinstance(kwargs['exc_info'][1], TypeError):
            self.set_status(400)
            self.write_object({
                'code': None,
                'message': str(kwargs['exc_info'][1]),
                'errors': None,
                'extra':  None,
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
        if isinstance(obj, Pagination):
            self.write_pagination(obj)
            return
        self.write(
            utils.json_dumps(obj, indent=4, sort_keys=True),
        )

    def write_pagination(self, pagination):
        links = pagination.links_header_format(
            urljoin(
                '{}://{}'.format(
                    self.request.protocol,
                    self.request.host,
                ), 
                self.request.path
            ), 
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

    @gen.coroutine
    def es(self, url, query={}, body={}):
        http_client = AsyncHTTPClient()         
        if not url.startswith('/'):
            url = '/'+url
        for arg in query:
            if not isinstance(query[arg], list):
                query[arg] = [query[arg]]
        try:
            response = yield http_client.fetch(
                'http://{}{}?{}'.format(
                    config['api']['elasticsearch'],
                    url,
                    utils.url_encode_tornado_arguments(query) \
                        if query else '',
                ),
                method='POST' if body else 'GET',
                body=utils.json_dumps(body) if body else None,
            )
            return utils.json_loads(response.body)
        except HTTPError as e:
            try:
                extra = utils.json_loads(e.response.body)
            except:
                extra = {'error': e.response.body.decode('utf-8')}
            raise exceptions.Elasticsearch_exception(
                e.code,
                extra,
            )

    def get_current_user(self):
        auth = self.request.headers.get('Authorization', None)
        if not auth:
            return None
        bearer = auth.split(' ')
        if len(bearer) != 2:
            return None
        if bearer[0] != 'Bearer':
            raise tornado.web.HTTPError(400, 'Unrecognized token type')
        self.access_token = bearer[1]
        return User.get_from_token(self.access_token)

    def validate(self, schema, *arg, **args):
        try:
            if not isinstance(schema, schemas.Schema):            
                schema = schemas.Schema(schema, *arg, **args)    
            return schema(self.request.body)            
        except MultipleInvalid as e:
            data = []
            for error in e.errors:
                path = '.'.join(str(x) for x in error.path)
                data.append({
                    'field': path,
                    'message': error.msg,
                })
            raise exceptions.Validation_exception(errors=data)

    @gen.coroutine
    def log_exception(self, typ, value, tb):        
        tornado.web.RequestHandler.log_exception(self, typ, value, tb)
        if isinstance(value, exceptions.Elasticsearch_exception) and \
            value.status_code != 404:
            pass
        elif isinstance(value, tornado.web.HTTPError) and value.status_code < 500:
            return
        yield gen.Task(
            self.captureException,
            exc_info=(typ, value, tb),
            data=[value.extra] if isinstance(value, exceptions.API_exception) and \
                value.extra else None,
        )

    def get_sentry_user_info(self):
        return {
            'user': {
                'is_authenticated': True if self.current_user else False,
                'info': self.current_user.to_dict() if self.current_user else None,
            }
        }

    def get_sentry_data_from_request(self):
        return {
            'request': {
                'url': self.request.full_url(),
                'method': self.request.method,
                'query_string': self.request.query,
                'cookies': self.request.headers.get('Cookie', None),
                'headers': dict(self.request.headers),
            }
        }

    def options(self, *args, **kwargs):
        pass

    @authenticated(constants.LEVEL_EDIT_USER)
    def check_edit_another_user_right(self):
        pass

    def check_user_edit(self, user_id):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        return True

    @authenticated(constants.LEVEL_USER)
    def is_logged_in(self):
        pass

    def get_append_fields(self, allowed_append_fields):
        append_fields = list(
            filter(None, self.get_argument('append', '').split(','))
        )
        not_allowed = []
        for a in append_fields:
            if a not in allowed_append_fields:
                not_allowed.append(a)
        if not_allowed:
            raise exceptions.Append_fields_not_allowed(not_allowed)
        return append_fields

    image_remove_keys = (
        'relation_type',
        'relation_id',
    )
    def image_format(self, images):
        '''
        :param images: `dict` or list of `dict`
        '''
        if isinstance(images, list):
            for img in images:
                utils.keys_to_remove(
                    self.image_remove_keys,
                    img
                )
        else:
            utils.keys_to_remove(
                self.image_remove_keys,
                images
            )
        return images

    episode_remove_keys = (
        'show_id',
    )
    def episode_format(self, episodes):
        '''
        :param episodes: `episode()` or list of `episode()`
        '''
        if isinstance(episodes, list):
            for episode in episodes:
                utils.keys_to_remove(
                    self.episode_remove_keys,
                    episode
                )
        else:
            utils.keys_to_remove(
                self.episode_remove_keys,
                episodes
            )
        return episodes