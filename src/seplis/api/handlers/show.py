import logging
from seplis import schemas, tasks, utils, config
from seplis.api import constants, exceptions, models
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api.connections import database
from tornado.httpclient import HTTPError
from urllib.parse import urljoin

class Handler(base.Handler):

    allowed_append_fields = (
        'following',
        'user_watching',
        'user_rating',
    )
    async def get(self, show_id=None):
        if show_id:
            show = await self.get_show(show_id)
            self.write_object(show)
        else:
            q = self.get_argument('q', None)
            title = self.get_argument('title', None)
            title_suggest = self.get_argument('title_suggest', None)
            if q or title or title_suggest:
                shows = await self.search_show()
                self.write_object(shows)
            else:
                shows = await self.get_shows()
                if shows:
                    logging.info(self.request.query_arguments)
                    self.request.query_arguments['from_id'] = [str(shows[-1]['id'])]
                    logging.info(self.request.query_arguments)
                    n = urljoin(
                        config['api']['base_url'],
                        self.request.path
                    ) + '?' + utils.url_encode_tornado_arguments(self.request.query_arguments)
                    self.set_header('Link', f'<{n}>; rel="next"')
                self.write_object(shows)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def post(self, show_id=None):
        if show_id:
            raise exceptions.Parameter_restricted(
                'show_id must not be set when creating a new one'
            )
        show = await self._post()
        self.set_status(201)
        database.queue.enqueue(
            tasks.update_show,
            int(show['id']),
        )
        self.write_object(show) 

    @run_on_executor
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
    async def put(self, show_id): 
        show = await self.update(show_id=show_id, overwrite=True)
        self.write_object(show)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def patch(self, show_id):        
        show = await self.update(show_id=show_id, overwrite=False)
        self.write_object(show)

    @authenticated(constants.LEVEL_DELETE_SHOW)
    async def delete(self, show_id):
        await self._delete(show_id)
        self.set_status(204)

    @run_on_executor
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

    @run_on_executor
    def _delete(self, show_id):
        with new_session() as session:
            show = session.query(models.Show).get(show_id)
            session.delete(show)
            session.commit()

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

    async def get_show(self, show_id):
        append_fields = self.get_append_fields(self.allowed_append_fields)
        show = await self._get_show(show_id)
        if 'following' in append_fields:
            await self.append_following([show])
        if 'user_watching' in append_fields:
            await self.append_user_watching([show])
        if 'user_rating' in append_fields:
            await self.append_user_ratings([show])
        return show

    @run_on_executor
    def _get_show(self, show_id):
        with new_session() as session:
            show = session.query(models.Show).get(show_id)
            if not show:
                raise exceptions.Not_found('Unknown show')
            show = show.serialize()
            return show

    @run_on_executor
    def get_shows(self):
        from_id = int(self.get_argument('from_id', 0))
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        with new_session() as session:
            shows = session.query(models.Show).filter(
                models.Show.id > from_id,
            ).limit(per_page).all()
            return [show.serialize() for show in shows]

    async def search_show(self):
        append_fields = self.get_append_fields(self.allowed_append_fields)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))        
        sort = self.get_argument('sort', '_score:desc,title.length:asc,premiered:desc')
        fields = self.get_argument('fields', None)
        fields = list(filter(None, fields.split(','))) if fields else None
        req = {
            'size': per_page,
            'search_type': 'dfs_query_then_fetch',
        }
        body = self.build_query()
        if body:
            req['sort'] = sort
        if fields:
            if 'id' not in fields:
                fields.append('id')
            body['_source'] = fields

        result = await self.es(
            '/shows/show/_search',
            body=body,
            query=req,
        )
        shows = [r['_source'] for r in result['hits']['hits']]
        if 'following' in append_fields:
            await self.append_following(shows)
        if 'user_watching' in append_fields:
            await self.append_user_watching(shows)
        if 'user_rating' in append_fields:
            await self.append_user_ratings(shows)
        return shows

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
            'multi_match': {
                'query': title,
                'fields': ['title', 'alternative_titles'],
                'operator': 'and',
                'type': 'phrase',
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

    @run_on_executor
    def append_following(self, shows, user_id=None):
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        with new_session() as session:
            rows = session.query(models.Show_fan.show_id).filter(
                models.Show_fan.user_id == user_id,
            ).all()
            if not rows:
                return
            show_ids = set([r.show_id for r in rows])
        for show in shows:
            show['following'] = show['id'] in show_ids

    async def append_user_watching(self, shows, user_id=None):
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        await handler_utils.show.append_user_watching(user_id, shows)

    @run_on_executor
    def append_user_ratings(self, shows):
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
                models.User_show_rating.user_id == self.current_user.id,
                models.User_show_rating.show_id.in_(show_ids.keys()),
            ).all()
            if not q:
                return
            for s in q:
                show_ids[s.show_id]['user_rating'] = s.rating

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

    async def get(self, title, value):
        await Handler.get(self, self._get(title, value))

    async def put(self, title, value): 
        await Handler.put(self, self._get(title, value))

    async def patch(self, title, value): 
        await Handler.patch(self, self._get(title, value))

    def post(self, show_id=None):
        raise HTTPError(405)

    def delete(self, title, value): 
        raise HTTPError(405)     

class Update_handler(base.Handler):

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def post(self, show_id):
        job = database.queue.enqueue(
            tasks.update_show,
            int(show_id),
            timeout=600,
            result_ttl=0,
        )
        self.write_object({
            'job_id': job.id,
        })