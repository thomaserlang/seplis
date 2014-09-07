import logging
import json
import sqlalchemy.exc
from seplis.api.handlers import base
from tornado import gen, httpclient
from seplis.utils import json_dumps, json_loads, slugify, dict_update
from seplis import schemas, utils
from seplis.api import constants
from seplis.api import models
from seplis.decorators import new_session
from seplis.api import exceptions
from seplis.api.decorators import authenticated
from seplis.api.base.pagination import Pagination
from seplis.api.base.show import Shows, Show, Follow, Unfollow
from seplis.api.base.episode import Episode, Episodes
from seplis.api.base.tag import Tags
from seplis.api.base.description import Description
from seplis.connections import database
from seplis.config import config
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado import gen, concurrent
from datetime import datetime
from sqlalchemy import asc, desc, and_

class Handler(base.Handler):

    @gen.coroutine    
    def post(self, show_id=None):
        if show_id:
            raise exceptions.Parameter_must_not_be_set_exception('show_id must not be set when creating a new one')
        show_id = Show.create()
        self.set_status(201)
        if self.request.body:
            yield self.patch(show_id)
        else:
            self.write_object({
                'id': show_id,
            })

    @authenticated(0)
    @gen.coroutine
    def put(self, show_id):        
        show = yield self.put(show_id)
        self.write_object(
            show,
        )

    @concurrent.run_on_executor
    def _put(self, show_id):
        self.validate(schemas.Show_schema, required=True)
        if self.request.body['description']:
            description = Description(
                text=self.request.body['description']['text'] if self.request.body['description'] else None,
                url=self.request.body['description'].get('url') if self.request.body['description'] else None,
                title=self.request.body['description'].get('title') if self.request.body['description'] else None,
            )
        else:
            description = Description(None)
        show = Show(
            id=show_id,
            title=self.request.body['title'],
            description=description,
            premiered=self.request.body['premiered'],
            ended=self.request.body['ended'],
            externals=self.request.body['externals'],
            indices=self.request.body['indices'],
            status=self.request.body['status'],
        )
        if 'episodes' in self.request.body:
            self.put_episodes(
                show_id,
                self.request.body['episodes'],
            )
        show.save()
        return show

    @gen.coroutine
    def patch(self, show_id):
        show = yield self._patch(show_id)
        self.write_object(
            show
        )

    @concurrent.run_on_executor
    def _patch(self, show_id):
        self.validate(schemas.Show_schema)
        show = Show.get(show_id)
        if not show:
            raise exceptions.Show_unknown()
        if 'title' in self.request.body:
            show.title = self.request.body['title']
        if 'premiered' in self.request.body:
            show.premiered = self.request.body['premiered']
        if 'ended' in self.request.body:
            show.ended = self.request.body['ended']
        if 'externals' in self.request.body:
            show.externals.update(self.request.body['externals'])
        if 'indices' in self.request.body:
            show.indices.update(self.request.body['indices'])
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
        if 'status' in self.request.body:
            show.status = self.request.body['status']
        show.save()
        return show

    @gen.coroutine
    def get(self, show_id=None):
        if show_id:
            result = yield self.es('/shows/show/{}'.format(show_id))                
            if not result['found']:
                raise exceptions.Show_unknown()
            self.write_object(
                result['_source']
            )
        else:
            q = self.get_argument('q', None)
            per_page = int(self.get_argument('per_page', constants.per_page))
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
            p = Pagination(
                page=page,
                per_page=per_page,
                total=result['hits']['total'],
                records=[show['_source'] for show in result['hits']['hits']],
            )
            self.write_pagination(p)

    def put_episodes(self, show_id, episodes_dict):
        '''

        :param show_id: int
        :param episodes_dict: dict
        :returns boolean
        '''
        episodes = []
        for episode in episodes_dict:
            episodes.append(
                self._new_episode(episode)
            )
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
            if 'description' in episode_data:
                desc = episode_data['description']
                if desc:
                    if 'text' in desc:
                        episode.description.text = desc['text']
                    if 'title' in desc:
                        episode.description.title = desc['title']
                    if 'url' in desc:
                        episode.description.url = desc['url']
            if 'title' in episode_data:
                episode.title = episode_data['title']
            if 'air_date' in episode_data:
                episode.air_date = episode_data['air_date']
            if 'season' in episode_data:
                episode.season = episode_data['season']
            if 'episode' in episode_data:
                episode.episode = episode_data['episode']
            episodes.append(episode)
        return Episodes.save(show_id, episodes)

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

class Episodes_handler(base.Handler):

    def get(self, show_id):
        episodes = Episodes.get(
            show_id,
            from_=int(self.get_argument('from')),
            to=int(self.get_argument('to')),
        )
        if episodes == None:
            raise exceptions.Show_unknown()
        self.write_object(episodes)

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

class Episode_handler(Handler):

    def get(self, show_id, episode_number):
        episode = self.get_episode(show_id, episode_number)
        if not episode:
            raise exceptions.Not_found_exception('episode number {} not found for show id {}'.format(episode_number, show_id))    
        self.write(episode)            

    def post(self):
        raise HTTPError(405)

    @authenticated(0)
    def put(self, show_id, episode_number):
        if 'number' not in self.request.body:
            self.request.body['number'] = int(episode_number)
        self.validate(Episode_schema)
        current_episode = self.get_episode(show_id, episode_number)
        if current_episode:
            current_episode = current_episode
        else:
            current_episode = {}     
        episode = dict_update(
            current_episode, 
            self.request.body
        )    
        with new_session() as session:
            with self.redis.pipeline() as pipe:
                Show.update_episodes(session, pipe, show_id, [episode])
                pipe.execute()
            session.commit()
        self.write(episode)

    @authenticated(0)
    def delete(self, show_id, episode_number):
        episode = self.get_episode(show_id, episode_number)
        if not episode:
            raise exceptions.Not_found_exception('episode number: {} not found for show id: {}'.format(episode_number, show_id))    
        with new_session() as session:
            session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).delete()
            session.commit()
            self.set_status(204)
            self.finish()

    def get_episode(self, show_id, episode_number):
        '''
        Returns none if the episode was not found.

        :param show_id: int
        :param episode_number: int
        :returns: str 
            json format
        :raises: `tornado.web.HTTPError`
        '''
        if not show_id or not episode_number:
            raise exceptions.Parameter_missing_exception('missing show_id and/or episode_number')
        with new_session() as session:
            episode = session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                return None
            if episode.data:
                return episode.data
            else:
                return '{}'        

class Follow_handler(Handler):

    @authenticated(0)
    def put(self, show_id):
        Follow.follow(show_id, self.current_user.id)
        self.set_status(204)

    @authenticated(0)
    def delete(self, show_id):
        Unfollow.unfollow(show_id, self.current_user.id)
        self.set_status(204)

class Follows_handler(Handler):

    @authenticated(0)
    def get(self, user_id):
        per_page = self.get_argument('per_page', None)
        page = self.get_argument('page', None)        
        self.write_pagination(
            Shows.follows(
                user_id=user_id,
                per_page=int(per_page) if per_page else constants.per_page,
                page=int(page) if page else 1,
            )
        )