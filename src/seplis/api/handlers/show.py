import logging
from seplis import schemas, utils
from seplis.api import constants, exceptions, models, components
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, auto_session
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from tornado.httpclient import HTTPError
from tornado import gen, concurrent
from datetime import datetime
from collections import OrderedDict

class Handler(base.Handler):

    allowed_append_fields = (
        'is_fan',
        'user_watching',
    )
    @gen.coroutine
    def get(self, show_id=None):
        if show_id:
            shows = yield self.get_show(show_id)
            self.write_object(shows)
        else:
            show = yield self.get_shows()
            self.write_object(show)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine    
    def post(self, show_id=None):
        if show_id:
            raise exceptions.Parameter_restricted(
                'show_id must not be set when creating a new one'
            )
        show = yield self._post()
        self.set_status(201)
        self.write_object(show) 

    @concurrent.run_on_executor
    def _post(self):
        self.request.body = self.validate(schemas.Show_schema)
        with new_session() as session:
            show = models.Show()
            session.add(show)
            session.flush()
            self._update(
                show=show, 
                overwrite=False,
                session=session,
            )
            session.commit()
            return show.serialize()

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def put(self, show_id): 
        show = yield self.update(show_id=show_id, overwrite=True)
        self.write_object(show)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def patch(self, show_id):        
        show = yield self.update(show_id=show_id, overwrite=False)
        self.write_object(show)

    @concurrent.run_on_executor
    def update(self, show_id=None, overwrite=False):
        self.request.body = self.validate(schemas.Show_schema)
        with new_session() as session: 
            show = session.query(models.Show).get(show_id)
            if not show:
                raise exceptions.Not_found('unknown show')
            self._update(
                session,
                show,
                overwrite=overwrite,
            )    
            session.commit()
            return show.serialize()

    def _update(self, session, show, overwrite=False):
        self._add_poster_image(show, session)
        self.flatten_request(self.request.body, 'description', 'description')
        self.flatten_request(self.request.body, 'importers', 'importer')
        if overwrite:
            for key in constants.IMPORTER_TYPE_NAMES:
                setattr(show, 'importer_'+key, None)
        if 'episodes' in self.request.body:
            episodes = self.request.body.pop('episodes')
            self.patch_episodes(
                session,
                show.id,
                episodes,
            )
            session.flush()
            show.update_seasons()
        self.update_model(
            model_ins=show,
            new_data=self.request.body,
            overwrite=overwrite,
        )

    def _add_poster_image(self, show, session):
        poster_image_id = self.request.body.get('poster_image_id')
        if not poster_image_id or \
            poster_image_id == show.poster_image_id:
            return
        show.poster_image = session.query(models.Image).get(
            poster_image_id
        )
        if not show.poster_image:
            raise exceptions.Image_unknown()

    def patch_episodes(self, session, show_id, episodes_dict):        
        '''

        :param show_id: int
        :param episodes_dict: dict
        :returns boolean
        '''
        episodes = []
        numbers = [episode['number'] for episode in episodes_dict]
        ep_g = {episode['number']: episode for episode in episodes_dict}
        episodes = session.query(models.Episode).filter(
            models.Episode.show_id == show_id,
            models.Episode.number.in_(numbers),
        ).all()
        for episode in episodes:
            numbers.remove(episode.number)
            self.flatten_request(ep_g[episode.number], 'description', 'description')
            self.update_model(
                model_ins=episode,
                new_data=ep_g[episode.number],
                overwrite=False,
            )
        for number in numbers:
            episode = models.Episode(
                show_id=show_id,
                number=number,
            )
            session.add(episode)
            self.flatten_request(ep_g[episode.number], 'description', 'description')
            self.update_model(
                model_ins=episode,
                new_data=ep_g[episode.number],
                overwrite=False,
            )

    @gen.coroutine
    def get_show(self, show_id):
        append_fields = self.get_append_fields(self.allowed_append_fields)
        result = yield self.es('/shows/show/{}'.format(show_id))                
        if not result['found']:
            raise exceptions.Show_unknown()
        show = result['_source']
        if 'is_fan' in append_fields:
            self.append_is_fan([show])
        if 'user_watching' in append_fields:
            yield self.append_user_watching([show])
        if show['poster_image']:
            self.image_wrapper(result['_source']['poster_image'])
        return show

    @gen.coroutine
    def get_shows(self, show_ids=None):
        append_fields = self.get_append_fields(self.allowed_append_fields)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', '_score:desc,title.length:asc,premiered:desc')
        fields = self.get_argument('fields', None)
        fields = list(filter(None, fields.split(','))) if fields else None
        req = {
            'from': ((page - 1) * per_page),
            'size': per_page,
            'sort': sort,
            'search_type': 'dfs_query_then_fetch',
        }
        body = self.build_query()
        if fields:
            if 'id' not in fields:
                fields.append('id')
            body['_source'] = fields
        if show_ids:
            body['filter'] = {
                'ids':{
                    'values': show_ids,
                }
            }        
        result = yield self.es(
            '/shows/show/_search',
            body=body,
            query=req,
        )
        shows = OrderedDict()
        for show in result['hits']['hits']:
            shows[show['_source']['id']] = show['_source']
            if show['_source'].get('poster_image'):
                self.image_wrapper(show['_source']['poster_image'])
        shows = list(shows.values())
        if 'is_fan' in append_fields:
            self.append_is_fan(shows)
        if 'user_watching' in append_fields:
            yield self.append_user_watching(shows)
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
            records=shows,
        )
        return p

    def build_query(self):
        """Builds a query from either argument: `q`, `title` or `title_suggest`."""
        q = self.get_argument('q', None)
        title = self.get_argument('title', None)
        title_suggest = self.get_argument('title_suggest', None)
        query = {}
        if q:
            query['query'] = self.build_query_query_string(q)
        elif title:
            query['query'] = self.build_query_title(title)
            query['track_scores'] = True
        elif title_suggest:
            query['query'] = self.build_query_title_suggest(title_suggest)
            query['track_scores'] = True
        return query

    def build_query_query_string(self, q):
        """Uses query string for a dynamic way of searching something specific 
        about a show.

        See: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
        """
        return {
             'query_string': {
                'fields': ['title', 'alternative_titles'],
                'query': q,                
                'fuzziness': 2,
            },
        }

    def build_query_title(self, title):
        """Searches after a specific title in `title` or `alternative_titles`."""
        return {
            'bool': {
                'should': [
                    {'match': {'title': {
                        'query': title, 
                        'operator': 'and',
                        'fuzziness': 1,
                    }}}, 
                    {'match': {'alternative_titles': {
                        'query': title, 
                        'operator': 'and',
                        'fuzziness': 1,
                    }}},
                ],
            }
        }

    def build_query_title_suggest(self, title):
        """Uses the `suggest` index, analyzed with nGram to match
        parts of the word in the `title` or `alternative_titles`.
        """
        return {
            'bool': {
                'should': [
                    {'match': {'title.suggest': {
                        'query': title, 
                        'operator': 'and',
                    }}}, 
                    {'match': {'alternative_titles.suggest': {
                        'query': title, 
                        'operator': 'and',
                    }}},
                ],
            }
        }

    def append_is_fan(self, shows, user_id=None):
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        is_fan = models.Show_fan.is_fan(
            user_id=user_id,
            show_id=[show['id'] for show in shows],
        )
        for f, show in zip(is_fan, shows):
            show['is_fan'] = f

    async def append_user_watching(self, shows, user_id=None):
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        await components.show.add_user_watching(user_id, shows)

class Multi_handler(base.Handler):

    def get(self, show_ids):
        ids = filter(None, show_ids.split(','))
        self.write_object(
            models.Shows.get(ids)
        )

class External_handler(Handler):

    def _get(self, title, value):
        show_id = models.Show.show_id_by_external(title, value)
        if not show_id:   
            raise exceptions.Not_found('show not found with external: {} with id: {}'.format(title, value))
        return show_id

    @gen.coroutine
    def get(self, title, value):
        yield Handler.get(self, self._get(title, value))

    @gen.coroutine
    def put(self, title, value): 
        yield Handler.put(self, self._get(title, value))

    @gen.coroutine
    def patch(self, title, value): 
        yield Handler.patch(self, self._get(title, value))

    def post(self, show_id=None):
        raise HTTPError(405)

    def delete(self, title, value): 
        raise HTTPError(405)     


        
class Fan_of_handler(Handler):

    @gen.coroutine
    def get(self, user_id):
        show_ids = database.redis.smembers(models.Show_fan._user_cache_name.format(
            user_id
        ))
        if show_ids:
            shows = yield self.get_shows(show_ids)
        else:
            shows = Pagination(
                page=int(self.get_argument('page', 1)),
                per_page=int(self.get_argument('per_page', constants.PER_PAGE)),
                total=0,
                records=[],
            )
        self.write_object(
            shows
        )

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def put(self, user_id, show_id):
        yield self._put(user_id, show_id)

    @concurrent.run_on_executor
    def _put(self, user_id, show_id):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        with new_session() as session:
            show = session.query(models.Show).get(show_id)
            if not show:
                raise exceptions.Show_unknown()
            show.become_fan(
                user_id,
            )
            session.commit()

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def delete(self, user_id, show_id):
        yield self._delete(user_id, user_id)

    @concurrent.run_on_executor
    def _delete(self, user_id, show_id):            
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        with new_session() as session:
            show = session.query(models.Show).get(show_id)
            if not show:
                raise exceptions.Show_unknown()
            show.unfan(
                user_id
            )
            session.commit()

    def post(self):
        raise HTTPError(405)

class Fans_handler(Fan_of_handler):

    def get(self, show_id):
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        pipe = database.redis.pipeline()
        name = models.Show_fan._show_cache_name.format(show_id)
        pipe.scard(name)
        pipe.sort(
            name=name,
            start=(page - 1) * per_page,
            num=per_page,
            by='nosort',
        )
        total_count, user_ids = pipe.execute()
        self.write_object(Pagination(
            page=page,
            per_page=per_page,
            total=total_count,
            records=models.User.get(user_ids),
        ))

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def put(self, show_id, user_id):        
        yield self._put(user_id=user_id, show_id=show_id)

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def delete(self, show_id, user_id):
        yield self._delete(user_id=user_id, show_id=show_id)

class Update_handler(base.Handler):

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def post(self, show_id):
        from seplis.tasks.update_show import update_show
        job = database.queue.enqueue(
            update_show, 
            self.access_token,
            int(show_id),
        )
        self.write_object({
            'job_id': job.id,
        })