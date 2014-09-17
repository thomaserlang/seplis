import logging
import json
import sqlalchemy.exc
from seplis.api.handlers import base
from tornado import gen, httpclient
from seplis.utils import json_dumps, json_loads, slugify, dict_update
from seplis.api import constants, models, exceptions
from seplis import schemas, utils
from seplis.decorators import new_session
from seplis.api.decorators import authenticated
from seplis.api.base.pagination import Pagination
from seplis.api.base.show import Show, Shows
from seplis.api.base.episode import Episode, Episodes, Watching
from seplis.api.base.tag import Tags
from seplis.api.base.description import Description
from seplis.connections import database
from seplis.config import config
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado import gen, concurrent
from datetime import datetime
from sqlalchemy import asc, desc, and_


class Handler(base.Handler):

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
            show = yield self._patch(
                show_id, 
                validate_show=False
            )
            self.write_object(show)
        else:
            self.write_object({
                'id': show_id,
            })

    @concurrent.run_on_executor
    def _post(self):
        self.validate(schemas.Show_schema)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def patch(self, show_id):
        show = yield self._patch(show_id)
        self.write_object(
            show
        )

    update_keys = (
        'title',
        'premiered',
        'ended',
        'externals',
        'indices',
        'status',
        'runtime',
        'genres',
        'alternate_titles',
    )

    @concurrent.run_on_executor
    def _patch(self, show_id, validate_show=True):
        if validate_show:
            self.validate(schemas.Show_schema)
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        self._update_keys(
            keys=self.update_keys,
            data=show.__dict__,
            new_data=self.request.body,
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
        if 'episodes' in self.request.body:
            self.patch_episodes(
                show_id,
                self.request.body['episodes'],
            )
        show.save()
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

    def _update_keys(self, keys, data, new_data):
        for key in keys:
            if key in new_data:
                if isinstance(new_data[key], dict):
                    data[key].update(new_data[key])
                elif isinstance(new_data[key], list):
                    data[key] = list(set(data[key] + new_data[key]))
                else:
                    data[key] = new_data[key]

    allowed_append_fields = (
        'is-fan'
    )

    @gen.coroutine
    def get(self, show_id=None):
        self.append_fields = self.get_append_fields(self.allowed_append_fields)
        if show_id:
            yield self.get_show(show_id)
        else:
            yield self.get_shows()

    @gen.coroutine
    def get_show(self, show_id):
        result = yield self.es('/shows/show/{}'.format(show_id))                
        if not result['found']:
            raise exceptions.Show_unknown()
        if 'is-fan' in self.append_fields:
            self.is_logged_in()
            result['_source']['is_fan'] = Show.is_fan(
                user_id=self.current_user.id,
                id_=show_id,
            )
        self.write_object(
            result['_source']
        )

    @gen.coroutine
    def get_shows(self):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', None)
        req = {
            'from': ((page - 1) * per_page),
            'size': per_page,
        }
        if q != None:
            req['q'] = q
        if sort:
            req['sort'] = sort
        result = yield self.es(
            '/shows/show/_search',
            **req
        )
        shows = {}
        for show in result['hits']['hits']:
            shows[show['_source']['id']] = show['_source']

        if 'is-fan' in self.append_fields:
            self.is_logged_in()
            show_ids = list(shows.keys())
            is_fan = Shows.is_fan(
                user_id=self.current_user.id,
                ids=show_ids,
            )
            for f, id_ in zip(is_fan, show_ids):
                shows[id_]['is_fan'] = f

        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
            records=list(shows.values()),
        )
        self.write_object(p)

class Multi_handler(base.Handler):

    def get(self, show_ids):
        ids = filter(None, show_ids.split(','))
        self.write_object(
            Shows.get(ids)
        )

class Suggest_handler(base.Handler):

    @gen.coroutine
    def get(self):
        q = self.get_argument('q')
        response = self.es.suggest(index='shows', body={
            'show': {
                'text': q,
                'completion': {
                    'field': 'title_suggest',
                }
            }
        })
        shows = [{'title': d['text'], 'id': d['payload']['show_id']} for show in response['show'] for d in show['options']]

        self.write_object(shows)


class External_handler(Handler):

    def _get(self, title, value):
        show_id = Show.get_id_by_external(title, value)
        if not show_id:   
            raise exceptions.Not_found_exception('show not found with external: {} with id: {}'.format(title, value))
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

    def get(self, user_id):
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'title:asc')

        self.write_pagination(
            Shows.get_fan_of(
                user_id=user_id,
                per_page=per_page,
                page=page,
                sort=sort,
            )
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