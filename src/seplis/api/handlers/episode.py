import logging
import json
from seplis.api.handlers import base
from seplis.api import constants,  exceptions
from seplis import schemas, utils
from seplis.api.decorators import authenticated, auto_session, auto_pipe, new_session
from seplis.config import config
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from seplis.api import models
from datetime import datetime, timedelta
from tornado import gen, web
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
            result['_source']['user_watched'] = models.Episode_watched.get(
                user_id=self.current_user.id,
                show_id=show_id,
                episode_number=number,
            )
        self.write_object(
            self.episode_wrapper(result['_source'])
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
            watched = models.Episode_watched.get(
                user_id=self.current_user.id,
                show_id=show_id,
                episode_number=numbers,
            )
            for w, number in zip(watched, numbers):
                episodes[number]['user_watched'] = w
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
            records=self.episode_wrapper(
                list(episodes.values())
            ),
        )
        self.write_object(p)

class Watched_handler(base.Handler):

    @authenticated(0)
    @gen.coroutine
    def put(self, user_id, show_id, episode_number):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        yield self._put(user_id, show_id, episode_number)

    @run_on_executor
    def _put(self, user_id, show_id, episode_number):
        self.validate(schemas.Episode_watched)
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            times = int(self.request.body.get('times', 1))
            episode.watched(
                user_id=user_id,
                times=times,
                position=int(self.request.body.get('position', 0)),
            )
            if times > 0:
                session.flush()
                models.Episode_watched.update_minutes_spent(
                    user_id=user_id,
                    session=session,
                    pipe=session.pipe,
                )
            session.commit()


    @authenticated(0)
    @gen.coroutine
    def delete(self, user_id, show_id, episode_number):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        yield self._delete(user_id, show_id, episode_number)

    @run_on_executor
    def _delete(self, user_id, show_id, episode_number):
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            episode.unwatch(user_id)
            session.flush()
            models.Episode_watched.update_minutes_spent(
                user_id=user_id,
                session=session,
                pipe=session.pipe,
            )
            session.commit()

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
        times = int(self.request.body.get('times', 1))

        with new_session() as session:
            episodes = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).all()
            for episode in episodes:
                episode.watched(user_id, times=times)     
            if times > 0:
                session.flush()
                models.Episode_watched.update_minutes_spent(
                    user_id=user_id,
                    session=session,
                    pipe=session.pipe,
                )
            session.commit()

    @authenticated(0)
    @gen.coroutine
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
        with new_session() as session:
            episodes = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).all()
            for episode in episodes:
                episode.unwatch(user_id)    
            session.flush()    
            models.Episode_watched.update_minutes_spent(
                user_id=user_id,
                session=session,
                pipe=session.pipe,
            )
            session.commit()

class Next_to_watch_handler(base.Handler):

    def get(self, user_id, show_id):
        episode_number = None
        try:
            w = models.Show_watched.get(
                user_id=user_id,
                show_id=show_id,
            )
            if w:
                return
            r = models.Episode_watched.recently(
                user_id=user_id,
                show_id=show_id,
                per_page=1,
            )
        finally:
            pass


class Play_servers_handler(base.Handler):

    @authenticated(0)
    @gen.coroutine
    def get(self, show_id, number):
        page = int(self.get_argument('page', 1))
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        servers = models.Play_server.by_user_id(
            user_id=self.current_user.id,
            access_to=True,
            page=page,
            per_page=per_page,
        )
        servers.records = yield self.get_play_ids(
            show_id,
            number,
            servers.records,
        )
        self.write_object(servers)

    @run_on_executor
    def get_play_ids(self, show_id, number, servers):
        results = []
        for server in servers:
            results.append({
                'play_id': web.create_signed_value(
                    secret=server['secret'],
                    name='play_id',
                    value=utils.json_dumps({
                        'show_id': int(show_id),
                        'number': int(number),
                    }),
                    version=2,
                ),
                'play_server': server,
            })
            server.pop('secret')
        return results