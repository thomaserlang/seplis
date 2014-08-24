import logging
from seplis.api.handlers import base
from seplis.api import constants, models, exceptions
from seplis import schemas, utils
from seplis.api.decorators import authenticated
from seplis.api.base.episode import Episode, Episodes
from seplis.connections import database
from seplis.api import models
from seplis.decorators import new_session
from seplis.config import config
from seplis.api.base.pagination import Pagination
from datetime import datetime
from sqlalchemy import asc, desc
from tornado.httpclient import AsyncHTTPClient
from tornado import gen 

class Handler(base.Handler):

    @gen.coroutine
    def get(self, show_id, number=None):
        http_client = AsyncHTTPClient()
        if number:
            response = yield http_client.fetch('http://{}/episodes/{}/{}'.format(
                config['elasticsearch'],
                show_id,
                number,
            ))
            result = utils.json_loads(response.body)        
            if not result['found']:
                raise exceptions.Episode_unknown()
            self.write_object(
                result['_source']
            )
        else:
            q = self.get_argument('q', None)
            per_page = int(self.get_argument('per_page', constants.per_page))
            page = int(self.get_argument('page', 1))
            sort = self.get_argument('sort', 'number:asc')
            req = {
                'from': [((page - 1) * per_page)],
                'size': [per_page],
                'sort': [sort],
            }
            if q != None:
                req['q'] = [q]
            response = yield http_client.fetch(
                'http://{}/episodes/{}/_search?{}'.format(
                    config['elasticsearch'],
                    show_id,
                    utils.url_encode_tornado_arguments(req)
                ),
            )
            result = utils.json_loads(response.body)
            p = Pagination(
                page=page,
                per_page=per_page,
                total=result['hits']['total'],
                records=[show['_source'] for show in result['hits']['hits']],
            )
            self.write_pagination(p)

    def put(self, show_id, number=None):
        if not number:
            self.put_multi(show_id, self.request.body)

class Watched_handler(base.Handler):

    @authenticated(0)
    def get(self, user_id, show_id=None, episode_number=None):
        self.get_shows_watched(user_id)

    def get_shows_watched(self, user_id):
        with new_session() as session:
            results = session.query(
                models.Show,
            ).filter(
                models.Show_watched.user_id == user_id,
                models.Show.id == models.Show_watched.show_id,
            ).order_by(
                desc(models.Show_watched.datetime),
                desc(models.Show.id)
            ).all()
            shows = []
            for show in results:
                if show.data:
                    shows.append(show.data)
            self.write_object(
                shows
            )

    @authenticated(0)
    def put(self, user_id, show_id, episode_number):        
        '''
        Updates information about how many times and where in the episode
        the user is.

        The show will be updated with what episode the user last watched
        and it's position in the episode.

        To update the position without incrementing the times watched,
        set the times to 0.
        '''
        if int(user_id) != self.current_user.id:
            self.check_user_right()
        with new_session() as session:
            # per show, episode
            ew = session.query(
                models.Episode_watched,
            ).filter(
                models.Episode_watched.show_id == show_id,
                models.Episode_watched.episode_number == episode_number,
                models.Episode_watched.user_id == user_id,
            ).first()
            if not ew:
                times = self.request.body.get('times', 1)
                if times < 0:
                    times = 0
                ew = models.Episode_watched(                    
                    show_id=show_id,
                    episode_number=episode_number,
                    user_id=user_id,                    
                    position=self.request.body.get('position', 0),
                    datetime=datetime.utcnow(),
                    times=times,
                )
                session.add(ew)
            else:
                times = ew.times + self.request.body.get('times', 1)
                if times < 0:
                    times = 0
                ew.position = self.request.body.get('position', 0)
                ew.datetime = datetime.utcnow()
                ew.times = times
            # per show
            self.set_show_last_watched(
                session,
                user_id,
                show_id,
                episode_number,
                ew,
            )
            session.commit()
            self.write_object({
                'user_id': user_id,
                'show_id': show_id,
                'episode_number': episode_number,
                'times': ew.times,
                'datetime': ew.datetime,
                'position': ew.position,
            })

    def set_show_last_watched(self, session, user_id, show_id, episode_number, episode_watched_query):
        sw = session.query(
            models.Show_watched,
        ).filter(
            models.Show_watched.show_id == show_id,
            models.Show_watched.episode_number == episode_number,
            models.Show_watched.user_id == user_id,
        )
        if not episode_watched_query:
            sw.delete()
            return
        sw = sw.first()
        if not sw:
            sw = models.Show_watched(                    
                show_id=episode_watched_query.show_id,
                episode_number=episode_watched_query.episode_number,
                user_id=episode_watched_query.user_id,                    
                position=episode_watched_query.position,
                datetime=episode_watched_query.datetime,
            )                
            session.add(sw)
        else:
            sw.episode_number = episode_watched_query.episode_number,
            sw.position = episode_watched_query.position,
            sw.datetime = episode_watched_query.datetime

    def get_last_watched_episode(self, session, user_id, show_id):
        ew = session.query(
            models.Episode_watched,
        ).filter(
            models.Episode_watched.show_id == show_id,
            models.Episode_watched.user_id == user_id,
        ).order_by(
            desc(models.Episode_watched.datetime)
        ).first()
        return ew

    @authenticated(0)
    def delete(self, user_id, show_id, episode_number):
        if int(user_id) != self.current_user.id:
            self.check_edit_another_user_right()
        with new_session() as session:
            w = session.query(
                models.Episode_watched,
            ).filter(
                models.Episode_watched.show_id == show_id,
                models.Episode_watched.episode_number == episode_number,
                models.Episode_watched.user_id == self.current_user.id,
            ).delete()
            if not w:
                raise exceptions.User_has_not_watched_this_episode()
            self.set_show_last_watched(
                session,
                user_id,
                show_id,
                episode_number,
                self.get_last_watched_episode(session, user_id, show_id)
            )
            session.commit()