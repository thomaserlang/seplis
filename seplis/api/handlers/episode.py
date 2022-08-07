import elasticsearch
import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api import constants, exceptions, models
from seplis import schemas, utils
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api.base.pagination import Pagination
from datetime import datetime, timedelta
from tornado import gen, web, concurrent
from collections import OrderedDict
from seplis.api.connections import database

class Handler(base.Handler):

    allowed_append_fields = (
        'user_watched'
    )
    async def get(self, show_id, number=None):
        self.append_fields = self.get_append_fields(
            self.allowed_append_fields
        )
        if number:
            await self.get_episode(show_id, number)
        else:
            await self.get_episodes(show_id)

    async def get_episode(self, show_id, number):
        try:
            result = await database.es_async.get(
                index='episodes',
                id=f'{show_id}-{number}',            
            )
        except elasticsearch.NotFoundError:
            raise exceptions.Not_found('the episode was not found')

        if 'user_watched' in self.append_fields:
            self.is_logged_in()
            with new_session() as session:
                ew = session.query(models.Episode_watched).filter(
                    models.Episode_watched.user_id == self.current_user.id,
                    models.Episode_watched.show_id == show_id,
                    models.Episode_watched.episode_number == number,
                ).first()
                result['_source']['user_watched'] = ew.serialize() if ew else None
        self.write_object(
            self.episode_wrapper(result['_source'])
        )

    async def get_episodes(self, show_id):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'number:asc')
        query = {
            'bool': {
                'must': [
                    {'term': {'show_id': show_id}}
                ]
            }
        }
        if q:
            query['bool']['must'].append({
                'query_string': {
                    'default_field': 'title',
                    'query': q,
                }
            })
        result = await database.es_async.search(
            index='episodes',
            query=query,
            from_=((page - 1) * per_page),
            size=per_page,
            sort=sort,
        )
        episodes = OrderedDict()
        for episode in result['hits']['hits']:
            episodes[episode['_source']['number']] = episode['_source']

        if 'user_watched' in self.append_fields:
            self.is_logged_in()
            await self.get_episode_watched(show_id, episodes)
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total']['value'],
            records=self.episode_wrapper(
                list(episodes.values())
            ),
        )
        self.write_object(p)

    @concurrent.run_on_executor
    def get_episode_watched(self, show_id, episodes):
        numbers = list(episodes.keys())
        with new_session() as session:
            ew = session.query(models.Episode_watched).filter(
                models.Episode_watched.user_id == self.current_user.id,
                models.Episode_watched.show_id == show_id,
                models.Episode_watched.episode_number.in_(numbers),
            ).all()
            for i in episodes:
                episodes[i]['user_watched'] = None
            for e in ew:
                episodes[e.episode_number]['user_watched'] = e.serialize()

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def delete(self, show_id, number):
        await self._delete(show_id, number)
        self.set_status(201)

    @concurrent.run_on_executor
    def _delete(self, show_id, number):
        with new_session() as session:
            e = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == number,
            ).first()
            if not e:
                raise exceptions.Not_found('unknown episode')
            session.delete(e)
            session.commit()

class Play_servers_handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    async def get(self, series_id, number):
        d = await self._get(series_id, number)
        self.write_object(d)

    @run_on_executor
    def _get(self, series_id, number):
        with new_session() as session:
            p = session.query(models.Play_server).filter(
                models.Play_access.user_id == self.current_user.id,
                models.Play_server.id == models.Play_access.play_server_id,
            ).options(
                sa.orm.undefer_group('secret')
            ).all()
            playids = []
            for s in p:
                playids.append({
                    'play_id': web.create_signed_value(
                        secret=s.secret,
                        name='play_id',
                        value=utils.json_dumps({
                            'type': 'series',
                            'series_id': int(series_id),
                            'number': int(number),
                        }),
                        version=2,
                    ).decode('utf-8'),
                    'play_url': s.url,
                })
            return playids