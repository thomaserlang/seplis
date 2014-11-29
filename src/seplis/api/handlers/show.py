import logging
from seplis import schemas
from seplis.api import constants, models, exceptions
from seplis.api.handlers import base
from seplis.api.decorators import authenticated
from seplis.api.base.pagination import Pagination
from seplis.api.base.show import Show, Shows
from seplis.api.base.episode import Episode, Episodes, Watching
from seplis.api.base.description import Description
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
        yield self._post()
        if show_id:
            raise exceptions.Parameter_must_not_be_set_exception(
                'show_id must not be set when creating a new one'
            )
        show_id = Show.create()
        self.set_status(201)
        if self.request.body:
            show = yield self._update(
                show_id, 
                validate_show=False
            )
            self.write_object(show)
        else:
            self.write_object({
                'id': show_id,
            })

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def put(self, show_id):
        show = yield self._update(show_id, overwrite=True)
        self.write_object(
            show
        )

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def patch(self, show_id):
        show = yield self._update(show_id)
        self.write_object(
            show
        )

    @concurrent.run_on_executor
    def _post(self):
        self.validate(schemas.Show_schema)

    update_keys = (
        'title',
        'premiered',
        'ended',
        'externals',
        'indices',
        'status',
        'runtime',
        'genres',
        'alternative_titles',
        'episode_type',
    )
    @concurrent.run_on_executor
    def _update(self, show_id, validate_show=True, overwrite=False):
        if validate_show:
            self.validate(schemas.Show_schema)
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        self._update_keys(
            keys=self.update_keys,
            data=show.__dict__,
            new_data=self.request.body,
            overwrite=overwrite,
        )
        if 'description' in self.request.body:
            desc = self.request.body['description']
            if desc:
                if 'text' in desc:
                    show.description.text = desc['text']
                if 'title' in desc:
                    show.description.title = desc['title']
                if 'url' in desc:
                    show.description.url = desc['url']
        if 'poster_image_id' in self.request.body:
            show.add_poster_image(self.request.body['poster_image_id'])
        if overwrite:
            for index, externals in constants.INDEX_TYPES:
                if index not in show.indices:
                    show.indices[index] = None
        if 'episodes' in self.request.body:
            self.patch_episodes(
                show_id,
                self.request.body['episodes'],
            )
        show.save()
        if show.poster_image:
            show.poster_image = self.image_format(
                show.poster_image.__dict__
            )
        return show

    update_episode_keys = (
        'title',
        'air_date',
        'season',
        'episode',
        'runtime',
    )
    def patch_episodes(self, show_id, episodes_dict):        
        '''

        :param show_id: int
        :param episodes_dict: dict
        :returns boolean
        '''
        episodes = []
        for episode_data in episodes_dict:
            episode = Episode.get(show_id, episode_data['number'])
            if not episode:
                episodes.append(
                    self._new_episode(episode_data)
                )
                continue
            self._update_keys(
                keys=self.update_episode_keys,
                data=episode.__dict__,
                new_data=episode_data,
            )
            if 'description' in episode_data:
                desc = episode_data['description']
                if desc:
                    if 'text' in desc:
                        episode.description.text = desc['text']
                    if 'title' in desc:
                        episode.description.title = desc['title']
                    if 'url' in desc:
                        episode.description.url = desc['url']
            episodes.append(episode)
        return Episodes.save(show_id, episodes)

    def _new_episode(self, episode):
        if 'description' in episode and episode['description']:
            description = Description(
                text=episode['description'].get('text'),
                url=episode['description'].get('url'),
                title=episode['description'].get('title'),
            )
        else:
            description = Description(None)
        return Episode(
            number=episode.get('number'),
            title=episode.get('title'),
            air_date=episode.get('air_date'),
            description=description,
            season=episode.get('season'),
            episode=episode.get('episode'),
            runtime=episode.get('runtime'),
        )

    def _update_keys(self, keys, data, new_data, overwrite=False):
        for key in keys:
            if key in new_data:
                if isinstance(new_data[key], dict):
                    if overwrite:
                        data[key] = new_data[key]
                    else:
                        data[key].update(new_data[key])
                elif isinstance(new_data[key], list):
                    if overwrite:
                        data[key] = new_data[key]
                    else:
                        data[key] = list(set(data[key] + new_data[key]))
                else:
                    data[key] = new_data[key]

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
            self.image_format(result['_source']['poster_image'])
        return show

    @gen.coroutine
    def get_shows(self, show_ids=None):
        append_fields = self.get_append_fields(self.allowed_append_fields)
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', '_score')
        fields = self.get_argument('fields', None)
        fields = list(filter(None, fields.split(','))) if fields else None
        req = {
            'from': ((page - 1) * per_page),
            'size': per_page,
            'sort': sort,
        }
        body = {}
        if fields:
            if 'id' not in fields:
                fields.append('id')
            body['_source'] = fields
        if q:
            body['query'] = {
                'query_string': {
                    'default_field': 'title',
                    'query': q,
                }
            }
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
            if 'poster_image' in show['_source'] and show['_source']['poster_image']:
                self.image_format(show['_source']['poster_image'])
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

    def append_is_fan(self, shows, user_id=None):
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        show_ids = [show['id'] for show in shows]
        is_fan = Shows.is_fan(
            user_id=user_id,
            ids=show_ids,
        )
        for f, show in zip(is_fan, shows):
            show['is_fan'] = f

    @gen.coroutine
    def append_user_watching(self, shows, user_id=None):
        pipe = database.redis.pipeline()
        show_ids = [show['id'] for show in shows]
        if not user_id:
            self.is_logged_in()
            user_id = self.current_user.id
        for id_ in show_ids:
            pipe.hgetall('users:{}:watching:{}'.format(
                user_id, 
                id_,
            ))
        watching = pipe.execute()
        # get episodes watching
        episode_ids = []
        for id_, w in zip(show_ids, watching):
            episode_ids.append(
                '{}-{}'.format(
                    id_, 
                    w['number'] if w else 0
                )
            )
        episodes = yield self.get_episodes(episode_ids)
        for w, show, episode in zip(watching, shows, episodes):
            if w:
                show['user_watching'] = {
                    'datetime': w['datetime'],
                    'position': int(w['position']),
                    'episode': episode,
                }
            else:
                show['user_watching'] = None

    @gen.coroutine
    def get_episodes(self, ids):
        episodes = yield self.es('/episodes/episode/_search', body={
            'filter': {
                'ids': {
                    'values': ids,
                }
            }
        })
        # how can I get elasticsearch to return the result in the
        # same order as it was requested?
        d = {'{}-{}'.format(e['_source']['show_id'], e['_source']['number']): 
            e['_source'] for e in episodes['hits']['hits']}
        result = []
        for id_ in ids:
            result.append(
                d.get(id_)
            )
        return result


class Multi_handler(base.Handler):

    def get(self, show_ids):
        ids = filter(None, show_ids.split(','))
        self.write_object(
            Shows.get(ids)
        )

class External_handler(Handler):

    def _get(self, title, value):
        show_id = Show.get_id_by_external(title, value)
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

class Fans_handler(Handler):

    def get(self, show_id):
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        self.write_object(
            show.get_fans(page=page, per_page=per_page)
        )

    @authenticated(constants.LEVEL_USER)
    def put(self, show_id, user_id):        
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        show.become_fan(
            user_id,
        )

    @authenticated(constants.LEVEL_USER)
    def delete(self, show_id, user_id):            
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        show.unfan(
            user_id
        )
        
class Fan_of_handler(Handler):

    @gen.coroutine
    def get(self, user_id):
        show_ids = database.redis.smembers('users:{}:fan_of'.format(
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
    def put(self, user_id, show_id):        
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        show.become_fan(
            user_id,
        )

    @authenticated(constants.LEVEL_USER)
    def delete(self, user_id, show_id):            
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        show.unfan(
            user_id
        )

    def post(self):
        raise HTTPError(405)

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