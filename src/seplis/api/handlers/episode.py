import logging
from seplis.api.handlers import base
from seplis.api import constants,  exceptions
from seplis import schemas, utils
from seplis.api.decorators import authenticated
from seplis.api.base.episode import Episode, Episodes, Watched
from seplis.decorators import auto_session, auto_pipe
from seplis.config import config
from seplis.api.base.pagination import Pagination
from datetime import datetime
from sqlalchemy import asc, desc
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado import gen
from tornado.concurrent import run_on_executor
from collections import OrderedDict

class Handler(base.Handler):

    allowed_append_fields = (
        'user_watched'
    )
    @gen.coroutine
    def get(self, show_id, number=None):
        self.append_fields = self.get_append_fields(self.allowed_append_fields)
        if number:
            yield self.get_episode(show_id, number)
        else:
            yield self.get_episodes(show_id)

    @gen.coroutine
    def get_episode(self, show_id, number):
        result = yield self.es('/episodes/episode/{}-{}'.format(
            show_id,
            number,
        ))
        if not result['found']:
            raise exceptions.Not_found('the episode was not found')
        if 'user_watched' in self.append_fields:
            self.is_logged_in()
            result['_source']['user_watched'] = Watched.get(
                user_id=self.current_user.id,
                show_id=show_id,
                number=number,
            )
        self.write_object(
            self.episode_format(result['_source'])
        )

    @gen.coroutine
    def get_episodes(self, show_id):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'number:asc')
        body = {
            'filter': {
                'term': {
                    'show_id': show_id,
                }
            }
        }
        if q:
            body.update({
                'query': {
                    'query_string': {
                        'default_field': 'title',
                        'query': q,
                    }
                }
            })
        result = yield self.es(
            '/episodes/episode/_search',
            query={
                'from': ((page - 1) * per_page),
                'size': per_page,
                'sort': sort,
            },           
            body=body,
        )

        episodes = OrderedDict()
        for episode in result['hits']['hits']:
            episodes[episode['_source']['number']] = episode['_source']

        if 'user_watched' in self.append_fields:
            self.is_logged_in()
            numbers = list(episodes.keys())
            watched = Watched.get(
                user_id=self.current_user.id,
                show_id=show_id,
                number=numbers,
            )
            for w, number in zip(watched, numbers):
                episodes[number]['user_watched'] = w
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
            records=self.episode_format(
                list(episodes.values())
            ),
        )
        self.write_object(p)

    remove_keys = (
        'show_id',
    )
    def episode_format(self, episodes):
        '''
        :param episodes: `episode()` or list of `episode()`
        '''
        if isinstance(episodes, list):
            for episode in episodes:
                utils.keys_to_remove(
                    self.remove_keys,
                    episode
                )
        else:
            utils.keys_to_remove(
                self.remove_keys,
                episodes
            )
        return episodes


class Watched_handler(base.Handler):

    @authenticated(0)
    def put(self, user_id, show_id, episode_number):        
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        self.validate(schemas.Episode_watched)
        episode = Episode.get(show_id, episode_number)
        if not episode:
            raise exceptions.Episode_unknown()
        episode.watched(
            user_id, 
            show_id,
            times=self.request.body.get('times', 1),
            position=self.request.body.get('position', 0),
        )

    @authenticated(0)
    def delete(self, user_id, show_id, episode_number):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        episode = Episode.get(show_id, episode_number)
        if not episode:
            raise exceptions.Episode_unknown()
        episode.unwatch(user_id, show_id)

class Watched_interval_handler(base.Handler):

    @authenticated(0)
    @gen.coroutine
    def put(self, user_id, show_id, from_, to):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        yield self._put(
            user_id, 
            show_id, 
            int(from_), 
            int(to),
        )

    @run_on_executor
    @auto_session
    @auto_pipe
    def _put(self, user_id, show_id, from_, to, 
        session=None, pipe=None):
        self.validate(schemas.Episode_watched)
        for episode_number in range(from_, to+1):
            episode = Episode.get(show_id, episode_number, session=session)
            if not episode:
                raise exceptions.Episode_unknown()
            episode.watched(
                user_id, 
                show_id,
                times=self.request.body.get('times', 1),
                position=self.request.body.get('position', 0),
                session=session,
                pipe=pipe,
            )

    @authenticated(0)
    def delete(self, user_id, show_id, from_, to):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        yield self._delete(
            user_id, 
            show_id, 
            int(from_), 
            int(to),
        )

    @run_on_executor
    @auto_session
    @auto_pipe   
    def _delete(self, user_id, show_id, from_, to,
        session=None, pipe=None):
        for episode_number in range(from_, to+1):
            episode = Episode.get(show_id, episode_number, session=session)
            if not episode:
                raise exceptions.Episode_unknown()
            episode.unwatch(
                user_id, 
                show_id,
                session=session,
                pipe=pipe,
            )

class Air_dates_handler(Handler):

    def get(self, user_id):        
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        offset_days = int(self.get_argument('offset_days', 1))
        days = int(self.get_argument('days', 7))
        self.write_object(
            Episodes.get_user_air_dates(
                user_id=user_id,
                per_page=per_page,
                page=page,
                offset_days=offset_days,
                days=days,
            )
        )