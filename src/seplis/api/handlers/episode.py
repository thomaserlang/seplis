import logging
from seplis.api.handlers import base
from seplis.api import constants, models, exceptions
from seplis import schemas, utils
from seplis.api.decorators import authenticated
from seplis.api.base.episode import Episode, Episodes, Watched
from seplis.connections import database
from seplis.api import models
from seplis.decorators import new_session
from seplis.config import config
from seplis.api.base.pagination import Pagination
from datetime import datetime
from sqlalchemy import asc, desc
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado import gen 

class Handler(base.Handler):

    allowed_append_fields = (
        'user_watching'
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
            raise exceptions.Episode_unknown()
        print(self.append_fields)
        if 'user_watching' in self.append_fields:
            print('hmm')
            self.is_logged_in()
            result['_source']['user_watching'] = Watched.get(
                user_id=self.current_user.id,
                show_id=show_id,
                number=number,
            )
        self.write_object(
            result['_source']
        )

    @gen.coroutine
    def get_episodes(self, show_id):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'number:asc')
        req = {
            'from': ((page - 1) * per_page),
            'size': per_page,
            'sort': sort,
            'q': 'show_id:{}'.format(show_id)
        }
        if q != None:
            req['q'] += ' AND {}'.format(q)
        result = yield self.es(
            '/episodes/episode/_search',
            **req
        )

        episodes = {}
        for episode in result['hits']['hits']:
            episodes[episode['_source']['number']] = episode['_source']

        if 'user_watching' in self.append_fields:
            self.is_logged_in()
            numbers = list(episodes.keys())
            watched = Watched.get(
                user_id=self.current_user.id,
                show_id=show_id,
                number=numbers,
            )
            for w, number in zip(watched, numbers):
                episodes[number]['user_watching'] = w

        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
            records=list(episodes.values()),
        )
        self.write_object(p)

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