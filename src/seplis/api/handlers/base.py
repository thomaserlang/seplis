from tornado import web, escape
import http.client, good, logging
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.attributes import flag_modified
from urllib.parse import urljoin
from seplis import utils
from seplis.api.decorators import new_session
from seplis.api.connections import database
from seplis.config import config
from seplis.api import models, exceptions, constants
from seplis.api.base.pagination import Pagination
from seplis.api.decorators import authenticated

class Handler(web.RequestHandler):

    def options(self, *args, **kwargs):
        self.set_status(204)

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
        self.set_header('Access-Control-Expose-Headers', 'ETag, Link, X-Total-Count, X-Total-Pages, X-Page')
        self.set_header('Access-Control-Max-Age', '86400')

    def update_model(self, model_ins, new_data, overwrite=False):
        '''Updates a SQLAlchemy model instance with a dict object.
        If a key's item is a list or dict the attribute will
        be marked as changed.

        :param models: SQLAlchemy instance
        :param new_data: dict
        :param overwrite: boolean
        '''
        try:
            for key in new_data:
                if not hasattr(model_ins, key):
                    continue
                if isinstance(new_data[key], dict) and not overwrite:
                    getattr(model_ins, key).update(new_data[key])
                    flag_modified(model_ins, key)
                elif isinstance(new_data[key], list) and not overwrite:
                    setattr(model_ins, key, 
                        list(set(
                            getattr(model_ins, key) + new_data[key]
                        ))
                    )
                    flag_modified(model_ins, key)
                else:
                    setattr(model_ins, key, new_data[key])
        except Exception as e:
            raise TypeError(
                'Update model failed for the following key: {} with error: {}'.format(
                    key, 
                    e.message,
                )
            )
            
    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            if isinstance(kwargs['exc_info'][1], exceptions.API_exception):
                self.write_object({
                    'code': kwargs['exc_info'][1].code,
                    'message': kwargs['exc_info'][1].message,
                    'errors': kwargs['exc_info'][1].errors,
                    'extra': kwargs['exc_info'][1].extra,
                })
                return
            elif isinstance(kwargs['exc_info'][1], OperationalError):
                self.set_status(503)
                self.write_object({
                    'code': 3000,
                    'message': 'lost connection to the database, please try again',
                    'errors': None,
                    'extra': None
                })
                return
        if 'exc_info' in kwargs and isinstance(kwargs['exc_info'][1], web.HTTPError) and kwargs['exc_info'][1].log_message:
            msg = kwargs['exc_info'][1].log_message
        else:
            msg = http.client.responses[status_code]
        self.write_object({
            'code': -1,
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
                config['api']['base_url'],
                self.request.path
            ), 
            self.request.query_arguments,
        )
        if links:
            self.set_header('Link', links)
        self.set_header('X-Total-Count', pagination.total)
        self.set_header('X-Total-Pages', pagination.pages)
        self.set_header('X-Page', pagination.page)
        self.write_object(pagination.records)

    @property
    def executor(self):
        return self.application.executor

    @property
    def redis(self):
        return database.redis

    async def es(self, url, query={}, body={}):
        return await database.es_get(url, query, body)

    def get_current_user(self):
        auth = self.request.headers.get('Authorization', None)
        if not auth:
            return None
        bearer = auth.split(' ')
        if len(bearer) != 2:
            return None
        if bearer[0] != 'Bearer':
            raise web.HTTPError(400, 'Unrecognized token type')
        self.access_token = bearer[1]
        user = models.User.by_token(self.access_token)
        if not user:
            return
        return utils.dotdict(user)

    def _validate(self, data, schema, **kwargs):
        try:
            return utils.validate_schema(schema, data, **kwargs)  
        except utils.Validation_exception as e:
            raise exceptions.Validation_exception(errors=e.errors)

    def validate(self, schema=None, **kwargs):
        if schema == None:
            schema = getattr(self, '__schema__', None)
            if schema == None:
                raise Exception('missing validation schema')
        return self._validate(
            self.request.body,
            schema,
            **kwargs
        )

    def validate_arguments(self, schema=None, **kwargs):
        if schema == None:
            schema = getattr(self, '__arguments_schema__', None)
            if schema == None:
                raise Exception('missing validation schema')
        return self._validate(
            escape.recursive_unicode(self.request.arguments),
            schema,
            **kwargs
        )

    @authenticated(constants.LEVEL_EDIT_USER)
    def check_edit_another_user_right(self):
        pass

    def check_user_edit(self, user_id):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        return True

    @authenticated(-100)
    def is_logged_in(self):
        pass

    def user_id_or_current(self, user_id):
        if not user_id or user_id == 'current':
            self.is_logged_in()
            user_id = self.current_user.id
        return user_id

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
        '_relation_type',
        '_relation_id',
    )
    def image_wrapper(self, images):
        _images = images if isinstance(images, list) else [images]
        for img in _images:
            utils.keys_to_remove(
                self.image_remove_keys,
                img,
            )
            img['url'] = config['api']['image_url'] + '/' + img['hash'] \
                if config['api']['image_url'] and img['hash'] else None
        return images

    episode_remove_keys = (
        'show_id',
    )
    def episode_wrapper(self, episodes):
        _episodes = episodes if isinstance(episodes, list) else [episodes]
        for episode in _episodes:
            utils.keys_to_remove(
                self.episode_remove_keys,
                episode
            )
        return episodes

    def user_wrapper(self, users):
        _users = users if isinstance(users, list) else [users]
        for user in _users:
            if not self.current_user or \
                ((self.current_user.level < constants.LEVEL_SHOW_USER_EMAIL) and \
                    (self.current_user.id != user['id'])):
                user.pop('email')
                user.pop('level')
        return users

    def show_wrapper(self, shows):
        _shows = shows if isinstance(shows, list) else [shows]
        for show in _shows:
            if show['poster_image']:
                self.image_wrapper(show['poster_image'])
        return shows

    def flatten_request(self, data, key, parent_key):
        if key in data:
            if data[key]:
                d = utils.flatten(
                    data[key],
                    parent_key=parent_key,
                )
                data.update(d)
            data.pop(key)

    async def get_shows(self, show_ids):
        '''Returns a list of shows. Id's that was not found
        will be appended as `None`.

        :param show_ids: list of int
        :returns: list of dict
        '''
        if not show_ids:
            return []
        result = await self.es('/shows/show/_mget', body={
            'ids': show_ids
        })
        return [d.get('_source') for d in result['docs']]

    async def get_episodes(self, episode_ids):
        '''Returns a list of episodes. Id's that was not found
        will be appended as `None`.

        :param episode_ids: list of str
            {show_id}-{episode_number}
        :returns: list of dict
        '''
        result = await self.es('/episodes/episode/_mget', body={
            'ids': episode_ids
        })
        return [d.get('_source') for d in result['docs']]

    def expand_user_rating(self, shows, user_id):
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        with new_session() as session:
            show_ids = {}
            for s in shows:
                s['user_rating'] = None
                show_ids[s['id']] = s
            q = session.query(
                models.User_show_rating.rating, 
                models.User_show_rating.show_id,
            ).filter(
                models.User_show_rating.user_id == user_id,
                models.User_show_rating.show_id.in_(show_ids.keys()),
            ).all()
            if not q:
                return
            for s in q:
                show_ids[s.show_id]['user_rating'] = s.rating

class Pagination_handler(Handler):

    __arguments_schema__ = good.Schema({
        'per_page': good.Any(
            good.All(
                [good.All(good.Coerce(int), good.Range(min=1))],
                good.Length(max=1),
            ),
            good.Default([constants.PER_PAGE])
        ),
        'page': good.Any(
            good.All(
                [good.All(good.Coerce(int), good.Range(min=1))],
                good.Length(max=1),
            ),
            good.Default([1])
        ),
    }, default_keys=good.Required, extra_keys=good.Allow,)

    def get(self, *args, **kwargs):
        args = self.validate_arguments(Pagination_handler.__arguments_schema__)
        self.per_page = args.pop('per_page', [0])[0]
        self.page = args.pop('page', [0])[0]
        self.request.arguments.pop('per_page', None)
        self.request.arguments.pop('page', None)