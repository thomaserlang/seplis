import logging
from seplis.decorators import new_session, auto_session, auto_pipe
from seplis.connections import database
from seplis.api.base.pagination import Pagination
from seplis.api.base.description import Description
from seplis.api.base.show import Show
from seplis.api import exceptions, constants, models
from seplis import utils
from sqlalchemy import asc, desc
from datetime import datetime, timedelta

class Episode(object):

    def __init__(self, number, title=None, air_date=None, 
                 description=None, season=None, episode=None,
                 runtime=None):
        '''

        :param title: str
        :param number: int
        :param air_date: `datetime.date()`
        :param description: `seplis.api.base.description.Description()`
        :param season: int
        :param episode: int
        :param runtime: int
        '''
        self.number = number
        self.title = title
        self.air_date = air_date
        self.description = description
        self.season = season
        self.episode = episode
        self.runtime = runtime

    def to_dict(self):
        return self.__dict__

    @auto_session
    def save(self, show_id, session=None):        
        '''

        :param show_id: int
        :param session: SQLAlchemy session
        :returns: boolean
        '''
        episode = models.Episode(
            show_id=show_id,
            number=self.number,
            title=self.title,
            air_date=self.air_date,
            description_text=self.description.text if self.description else None,
            description_title=self.description.title if self.description else None,
            description_url=self.description.url if self.description else None,
            season=self.season,
            episode=self.episode,
        )
        session.merge(episode)
        self.to_elasticsearch(show_id)

    def to_elasticsearch(self, show_id):
        self.show_id = show_id
        database.es.index(
            index='episodes',
            doc_type='episode',
            id='{}-{}'.format(show_id, self.number),
            body=utils.json_dumps(self),
        )
        self.__dict__.pop('show_id')

    @auto_session
    @auto_pipe
    def watched(self, user_id, show_id,
        times=1, position=0, session=None, pipe=None):
        '''        
        Set an episode as watched a number of `times`.

        To set the position without incrementing the 
        times watched set the `times` variable to 0.

        :param user_id: int
        :param show_id: int
        :param times: int
        :param position: int
        '''
        Watched.watched(
            user_id=user_id,
            show_id=show_id,
            number=self.number,
            times=times,
            position=position,
            session=session,
            pipe=pipe,
        )

    @auto_session
    @auto_pipe
    def unwatch(self, user_id, show_id, session=None, pipe=None):
        '''
        Totally removes a watched episode.
        To decrement the number of times watched use the `watched` 
        method with `times` set to `-1`.

        :param user_id: int
        :param show_id: int
        '''
        Watched.unwatch(
            user_id=user_id,
            show_id=show_id,
            number=self.number,
            session=session,
            pipe=pipe,
        )

    @classmethod
    def _format_from_row(cls, row):
        if not row:
            return None
        return Episode(
            number=row.number,
            title=row.title,
            air_date=row.air_date,
            description=Description(
                text=row.description_text,
                title=row.description_title,
                url=row.description_url,
            ),
            season=row.season,
            episode=row.episode,
            runtime=row.runtime,
        )

    @classmethod
    @auto_session
    def get(cls, show_id, number, session=None):
        episode = session.query(
            models.Episode,
        ).filter(
            models.Episode.show_id == show_id,
            models.Episode.number == number,
        ).first()
        return cls._format_from_row(
            episode
        )

class Watched(object):

    def __init__(self, times, position, datetime_):
        '''

        :param times: int
        :param position: int
        :param datetime: str (ISO8601)
        '''
        self.times = times
        self.position = position
        self.datetime = datetime_

    def to_dict(self):
        return self.__dict__

    @classmethod
    def get(cls, user_id, show_id, number):
        '''

        :param user_id: int
        :param show_id: int
        :param number: int of list of int
        :returns: `Watched()` or list of `Watched()`
        '''
        pipe = database.redis.pipeline()
        numbers = number
        if not isinstance(number, list):
            numbers = [number]
        for n in numbers:
            pipe.hgetall('users:{}:watched:{}-{}'.format(user_id, show_id, number))
        results = pipe.execute()
        if not results and not isinstance(number, list):
            return None
        watched = []
        for w in results:
            if not w:
                watched.append(None)
                continue
            watched.append(cls(
                times=int(w['times']),
                position=int(w['position']),
                datetime_=w['datetime'],
            ))
        if isinstance(number, list):
            return watched
        return watched[0]

    @classmethod
    @auto_session
    @auto_pipe
    def watched(cls, user_id, show_id, number, times, position,
        session=None, pipe=None):
        '''

        :returns: `Watched()`
        '''
        # per show, episode
        ew = session.query(
            models.Episode_watched,
        ).filter(
            models.Episode_watched.show_id == show_id,
            models.Episode_watched.episode_number == number,
            models.Episode_watched.user_id == user_id,
        ).first()
        if not ew:
            if times < 0:
                times = 0
            ew = models.Episode_watched(                    
                show_id=show_id,
                episode_number=number,
                user_id=user_id,                    
                position=position,
                datetime=datetime.utcnow(),
                times=times,
            )
            session.add(ew)
        else:
            times = ew.times + times
            if times < 0:
                times = 0
            ew.position = position
            ew.datetime = datetime.utcnow()
            ew.times = times
        # per show
        cls._set_currently_watching(
            user_id,
            show_id,
            number,
            ew,
            session=session,
        )
        cls.cache_watched(
            user_id=user_id,
            show_id=show_id,
            number=number,
            times=ew.times,
            position=ew.times,
            datetime_=ew.datetime,
        )
        return cls(
            times=ew.times,
            position=ew.position,
            datetime_=ew.datetime,
        )

    @classmethod
    @auto_session
    @auto_pipe
    def unwatch(cls, user_id, show_id, number, session=None, pipe=None):
        '''

        :returns: boolean
        :raises: `exceptions.User_has_not_watched_this_episode()`
        '''
        w = session.query(
            models.Episode_watched,
        ).filter(
            models.Episode_watched.show_id == show_id,
            models.Episode_watched.episode_number == number,
            models.Episode_watched.user_id == user_id,
        ).delete()
        if not w:
            raise exceptions.User_has_not_watched_this_episode()
        cls._set_currently_watching(
            user_id,
            show_id,
            number,
            cls._get_latest_watched(
                user_id, 
                show_id, 
                session=session
            ),
            session=session,
        )
        pipe.delete('users:{}:watched:{}-{}'.format(user_id, show_id, number))
        return True

    @classmethod
    @auto_pipe
    def cache_watched(self, user_id, show_id, number,
        times, position, datetime_, pipe=None):
        name = 'users:{}:watched:{}-{}'.format(user_id, show_id, number)
        pipe.hset(
            name,
            'times',
            times,
        )        
        pipe.hset(
            name,
            'position',
            times,
        )
        pipe.hset(
            name,
            'datetime',
            datetime_.isoformat()+'Z',
        )

    @classmethod
    def _get_latest_watched(cls, user_id, show_id, session):
        '''

        :param user_id: int
        :param show_id: int
        :returns: SQLAlchemy query
        '''
        ew = session.query(
            models.Episode_watched,
        ).filter(
            models.Episode_watched.show_id == show_id,
            models.Episode_watched.user_id == user_id,
        ).order_by(
            desc(models.Episode_watched.datetime)
        ).first()
        return ew

    @classmethod
    def _set_currently_watching(cls, user_id, show_id, number, 
        episode_watched_query, session):
        '''
        Sets the episode as currently watching for the show.

        :param user_id: int
        :param show_id: int
        :param episode_watched_query: SQLAlchemy query
        '''
        print(user_id, show_id, number)
        sw = session.query(
            models.Show_watched,
        ).filter(
            models.Show_watched.show_id == show_id,
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

class Episodes(object):

    @classmethod
    @auto_session
    def save(cls, show_id, episodes, session=None):
        '''
        Save a list of episodes.

        :param show_id: int
        :param episodes: [`Episode()`]
        :returns boolean
        '''
        for episode in episodes:
            episode.save(show_id, session)
        return True

    @classmethod
    @auto_session
    def get_user_air_dates(cls, user_id, offset_days=1, days=7, 
        page=1, per_page=constants.PER_PAGE, session=None):
        query = session.query(
            models.Show,
            models.Episode,
        ).filter(
            models.Show_fan.user_id == user_id,
            models.Episode.show_id == models.Show_fan.show_id,
            models.Episode.air_date >= (datetime.utcnow().date() - timedelta(days=offset_days)),
            models.Episode.air_date <= (datetime.utcnow().date() + timedelta(days=days)),
            models.Show.id == models.Episode.show_id,
        )
        pagination = Pagination.from_query(
            query,
            count_field=models.Episode.show_id,
            page=page,
            per_page=per_page,
        )
        query = query.limit(
            int(per_page),
        ).offset(
            int(page-1) * int(per_page),
        )
        episodes = []
        for row in query.all():
            episodes.append({
                'show': Show._format_from_row(row.Show),
                'episode': Episode._format_from_row(row.Episode),
            })
        pagination.records = episodes
        return pagination