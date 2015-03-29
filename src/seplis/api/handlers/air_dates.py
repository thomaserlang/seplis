import logging
import json
from seplis.api.handlers import base
from seplis.api import constants,  exceptions
from seplis import schemas, utils
from seplis.api.decorators import authenticated
from seplis.config import config
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from seplis.api import models
from datetime import datetime, timedelta
from tornado import gen, web
from tornado.concurrent import run_on_executor
from collections import OrderedDict

class Air_dates_handler(base.Handler):

    @gen.coroutine
    def get(self, user_id):        
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        offset_days = int(self.get_argument('offset_days', 1))
        days = int(self.get_argument('days', 7))
        result = []
        episode_count = 0
        

            shows = yield self.es('/shows/show/_search',
                body={
                    'filter': {
                        'ids': {
                            'values': list(set([episode['show_id'] \
                                for episode in episodes])),
                        }
                    }
                },
                query={
                    'size': 1000,
                    'from': 0,
                }
            )
            shows = {str(show['_source']['id']): show['_source'] \
                for show in shows['hits']['hits']}
            for episode in episodes:
                result.append({
                    'show': shows[str(episode['show_id'])],
                    'episode': self.episode_wrapper(episode),
                })
        self.write_object(
            Pagination(
                page=page,
                per_page=per_page,
                total=episode_count,
                records=result,
            )
        )


    @gen.coroutine
    def get_episodes(self):
        should_be = self.get_should_filter(user_id)
        if should_be:
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
                    'from': ((page - 1) * per_page),
                    'size': per_page,
                    'sort': 'air_date:asc,show_id:asc,number:asc',
                },
            )
            episode_count = episodes['hits']['total']
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
