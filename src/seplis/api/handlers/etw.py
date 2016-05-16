import logging
from seplis.api.handlers import base
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated
from seplis import config
from tornado import gen, web
from tornado.concurrent import run_on_executor
from datetime import datetime

class Handler(base.Handler):

    @gen.coroutine
    def get(self, user_id):
        grouped = yield self.get_episodes(user_id)
        if grouped:
            shows = yield self.get_shows(list(grouped.keys()))
            for show, episodes in zip(shows, list(grouped.values())):
                show['next_episode'] = episodes[0]
                show['total_next_episodes'] = len(episodes)
            shows = sorted(shows, key=lambda d: d['title'])
        else:
            shows = []
        self.write_object(shows)        

    @gen.coroutine
    def get_episodes(self, user_id):
        show_ids = models.Show_fan.get_all(user_id)
        shows_watched = models.Episode_watched.cache_get_show(
            user_id=user_id,
            show_id=show_ids,
        )
        if not show_ids:
            return {}
        def ep_number(watched):
            if not watched:
                return 0
            if not watched['completed']:
                return watched['episode_number'] - 1
            return watched['episode_number']
        episodes = yield self.es('/episodes/episode/_search',
            body={
                'filter': {
                    'bool': {
                        'should': [
                            {
                                'bool': {
                                    'must': [
                                        {'term': {
                                            'show_id': id_,
                                        }},
                                        {'range': {
                                            'number': {
                                                'gt': ep_number(watched),
                                            },
                                        }},
                                    ],
                                },
                            } for id_, watched in zip(show_ids, shows_watched)],
                        'must': {
                            'range': {
                                'air_date': {
                                    'lte': datetime.utcnow().date(),
                                },
                            },
                        },
                    },
                },
                'sort': [
                    {'number': {'order': 'asc'}},
                ],
                'size': 10000,
            },
        )
        grouped = {}
        for d in episodes['hits']['hits']:
            ep = d['_source']
            show = grouped.setdefault(str(ep.pop('show_id')), [])
            show.append(ep)
        return grouped
