import logging
import json
from seplis.api.handlers import base
from seplis.api import constants, exceptions
from seplis import schemas, utils
from seplis.api.decorators import authenticated
from seplis.config import config
from seplis.api.connections import database
from seplis.api import models
from datetime import datetime, timedelta
from tornado import gen, web
from tornado.concurrent import run_on_executor

class Handler(base.Handler):

    @gen.coroutine
    def get(self, user_id):        
        episodes = yield self.get_episodes(user_id)
        if not episodes:
            self.write_object([])
            return
        ids = []
        [ids.append(episode['show_id']) for episode in episodes \
            if episode['show_id'] not in ids]
        shows = yield self.get_shows(ids)
        d = {show['id']: show for show in shows}
        for ep in episodes:
            show = d[ep['show_id']]
            show.setdefault('episodes', [])
            show['episodes'].append(
                self.episode_wrapper(ep)
            )
        self.write_object(shows)

    @gen.coroutine
    def get_episodes(self, user_id):        
        offset_days = int(self.get_argument('from_date', 1))
        days = int(self.get_argument('to_date', 7))
        should_be = self.get_should_filter(user_id)
        if not should_be:
            return []
        episodes = yield self.es('/episodes/episode/_search',
            body={
                'filter': {
                    'bool': {
                        'should': should_be,
                        'must': {
                            'range': {
                                'air_date': {
                                    'gte': (datetime.utcnow().date() - \
                                        timedelta(days=offset_days)).isoformat(),
                                    'lte': (datetime.utcnow().date() + \
                                        timedelta(days=days)).isoformat(),
                                }
                            }
                        }
                    }
                }
            },
            query={
                'from': 0,
                'size': 1000,
                'sort': 'air_date:asc,show_id:asc,number:asc',
            },
        )
        return [episode['_source'] \
            for episode in episodes['hits']['hits']]

    def get_should_filter(self, user_id):
        show_ids = database.redis.smembers(models.Show_fan._user_cache_name.format(
            user_id
        ))
        return [{
            'term': {
                'show_id': int(id_),
            }
        } for id_ in show_ids]
