import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api import constants, exceptions, models
from seplis import schemas, utils
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api.base.pagination import Pagination
from datetime import datetime, timedelta
from tornado import gen, web, concurrent
from collections import OrderedDict

class Handler(base.Handler):

    allowed_append_fields = (
        'user_watched'
    )
    @gen.coroutine
    def get(self, show_id, number=None):
        self.append_fields = self.get_append_fields(
            self.allowed_append_fields
        )
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

    @gen.coroutine
    def get_episodes(self, show_id):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'number:asc')
        body = {
            'query': {
                'bool': {
                    'must': [
                        {'term': {'show_id': show_id}}
                    ]
                }
            }
        }
        if q:
            body['query']['bool']['must'].append({
                'query_string': {
                    'default_field': 'title',
                    'query': q,
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
            yield self.get_episode_watched(show_id, episodes)
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
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
    @gen.coroutine
    def delete(self, show_id, number):
        yield self._delete(show_id, number)
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
    async def get(self, show_id, number):
        d = await self._get(show_id, number)
        self.write_object(d)

    @run_on_executor
    def _get(self, show_id, number):
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
                            'show_id': int(show_id),
                            'number': int(number),
                        }),
                        version=2,
                    ),
                    'play_url': s.url,
                })
            return playids