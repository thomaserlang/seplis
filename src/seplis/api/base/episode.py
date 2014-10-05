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
            runtime=self.runtime,
        )
        session.merge(episode)
        self.to_elasticsearch(show_id)

    def to_elasticsearch(self, show_id):
        self.show_id = int(show_id)
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
        Removes a watched episode.
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
            pipe.hgetall('users:{}:watched:{}-{}'.format(user_id, show_id, n))
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
            _times = ew.times + times
            if _times < 0:
                _times = 0
                times = -ew.times
            ew.position = position
            ew.datetime = datetime.utcnow()
            ew.times = _times
        # per show
        cls._set_currently_watching(
            user_id,
            show_id,
            ew,
            session=session,
            pipe=pipe,
        )
        cls.cache_watched(
            user_id=user_id,
            show_id=show_id,
            number=number,
            times=times,
            position=ew.position,
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
            cls._get_latest_watched(
                user_id, 
                show_id, 
                session=session
            ),
            session=session,
            pipe=pipe,
        )
        name = 'users:{}:watched:{}-{}'.format(user_id, show_id, number)
        times = database.redis.hget(
            name=name,
            key='times',
        )
        cls.cache_stats(
            user_id=user_id, 
            times=-int(times),
        )
        pipe.delete(name)
        return True

    @classmethod
    @auto_pipe
    def cache_watched(cls, user_id, show_id, number,
        times, position, datetime_, pipe=None):
        name = 'users:{}:watched:{}-{}'.format(user_id, show_id, number)
        pipe.hincrby(
            name=name,
            key='times',
            amount=times,
        )        
        pipe.hset(
            name=name,
            key='position',
            value=position,
        )
        pipe.hset(
            name=name,
            key='datetime',
            value=datetime_.isoformat()+'Z',
        )
        if times > 0:
            cls.cache_stats(
                user_id=user_id,
                times=times,
                pipe=pipe,
            )

    @classmethod
    @auto_pipe
    def cache_stats(cls, user_id, times, pipe=None):
        pipe.hincrby(
            name='users:{}:stats'.format(user_id),
            key='episodes_watched',
            amount=times,
        )

    @classmethod
    @auto_session
    @auto_pipe
    def cache_minutes_spent(cls, user_id, pipe=None, session=None):
        result = session.execute('''
            SELECT 
                sum(
                    if(isnull(e.runtime),
                        ifnull(s.runtime, 0),
                        e.runtime
                    ) * ew.times
                ) as minutes
            FROM
                episodes_watched ew,
                shows s,
                episodes e
            WHERE
                ew.user_id = :user_id
                    and e.show_id = ew.show_id
                    and e.number = ew.episode_number
                    and s.id = e.show_id;
        ''', {
            'user_id': user_id,
        })
        pipe.hset(
            name='users:{}:stats'.format(user_id),
            key='minutes_spent',
            value=result.first()['minutes'],
        )

    @classmethod
    def _get_latest_watched(cls, user_id, show_id, session):
        '''

        :param user_id: int
        :param show_id: int
        :returns: `models.Episode_watched()`
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
    def _set_currently_watching(cls, user_id, show_id, 
        episode_watched_query, session, pipe):
        '''
        Sets the episode as currently watching for the show.

        :param user_id: int
        :param show_id: int
        :param episode_watched_query: SQLAlchemy query
        '''
        sw = session.query(
            models.Show_watched,
        ).filter(
            models.Show_watched.show_id == show_id,
            models.Show_watched.user_id == user_id,
        )
        if not episode_watched_query:
            pipe.delete('users:{}:watching:{}'.format(user_id, show_id))
            sw.delete()
            return
        sw = sw.first()
        if not sw:
            sw = models.Show_watched(                    
                show_id=show_id,
                episode_number=episode_watched_query.episode_number,
                user_id=episode_watched_query.user_id,                    
                position=episode_watched_query.position,
                datetime=episode_watched_query.datetime,
            )                
            session.add(sw)
        else:
            sw.episode_number = episode_watched_query.episode_number
            sw.position = episode_watched_query.position
            sw.datetime = episode_watched_query.datetime
        cls.cache_currently_watching(
            user_id=user_id,
            show_id=show_id,
            number=episode_watched_query.episode_number,
            position=episode_watched_query.position,
            datetime_=episode_watched_query.datetime,
            pipe=pipe,
        )

    @classmethod
    @auto_pipe
    def cache_currently_watching(self, user_id, show_id, number,
        position, datetime_, pipe=None):
        name = 'users:{}:watching:{}'.format(user_id, show_id)        
        pipe.hset(
            name,
            'number',
            number,
        ) 
        pipe.hset(
            name,
            'position',
            position,
        )
        pipe.hset(
            name,
            'datetime',
            datetime_.isoformat()+'Z',
        )

class Watching(object):

    def __init__(self, number, position, datetime_):
        '''

        :param number: int
        :param position: int
        :param datetime: str (ISO8601)
        '''
        self.number = number
        self.position = position
        self.datetime = datetime_

    def to_dict(self):
        return self.__dict__

    @classmethod
    def get(cls, user_id, show_id):
        '''

        :param user_id: int
        :param show_id: int of list of int
        :returns: `Watched()` or list of `Watched()`
        '''
        pipe = database.redis.pipeline()
        show_ids = show_id
        if not isinstance(show_id, list):
            show_ids = [show_id]
        for n in show_ids:
            pipe.hgetall('users:{}:watching:{}'.format(user_id, show_id))
        results = pipe.execute()
        if not results and not isinstance(show_id, list):
            return None
        watching = []
        for w in results:
            if not w:
                watching.append(None)
                continue
            watching.append(cls(
                number=w['number'],
                position=int(w['position']),
                datetime_=w['datetime'],
            ))
        if isinstance(show_id, list):
            return watching
        return watching[0]


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