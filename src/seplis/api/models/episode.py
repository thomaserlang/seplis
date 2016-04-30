import logging
import sqlalchemy as sa
from .base import Base
from sqlalchemy import event, orm
from sqlalchemy.orm.attributes import get_history
from seplis import utils
from seplis.api.connections import database
from seplis.api.decorators import new_session, auto_pipe, auto_session
from seplis.api.base.pagination import Pagination
from seplis.api import exceptions, rebuild_cache, constants
from datetime import datetime

class Episode(Base):
    __tablename__ = 'episodes'

    show_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(200), unique=True)
    air_date = sa.Column(sa.Date)    
    description_text = sa.Column(sa.Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    season = sa.Column(sa.Integer)
    episode = sa.Column(sa.Integer)
    runtime = sa.Column(sa.Integer)

    def serialize(self):
        return {
            'show_id': self.show_id,
            'number': self.number,
            'title': self.title,
            'description': {
                'text': self.description_text,
                'title': self.description_title,
                'url': self.description_url,
            },
            'season': self.season,
            'episode': self.episode,
            'runtime': self.runtime,
            'air_date': self.air_date,
        }

    def to_elasticsearch(self):
        '''Sends the episodes's info to ES.

        This method is automatically called after update or insert.
        ''' 
        self.session.es_bulk.append({
            '_index': 'episodes',
            '_type': 'episode',
            '_id': '{}-{}'.format(self.show_id, self.number),
            '_source': utils.json_dumps(self.serialize()),
        })

    def after_upsert(self):
        self.to_elasticsearch()

    def after_delete(self):
        ews = self.session.query(Episode_watched).filter(
            Episode_watched.show_id == self.show_id,
            Episode_watched.episode_number == self.number,
        ).all()
        for ew in ews:
            self.session.delete(ew) 
        self.session.es_bulk.append({
            '_op_type': 'delete',
            '_index': 'episodes',
            '_type': 'episode',
            '_id': '{}-{}'.format(self.show_id, self.number),
        })

    def unwatch(self, user_id):
        '''Removes this episode from the user's watched list.

        :param user_id: int
        '''
        w = self.session.query(
            Episode_watched,
        ).filter(
            Episode_watched.show_id == self.show_id,
            Episode_watched.episode_number == self.number,
            Episode_watched.user_id == user_id,
        ).first()
        if not w:
            raise exceptions.User_episode_not_watched()
        self.session.delete(w)

    def watched(self, user_id, times=1, position=0):
        '''Marks the episode as watched for the user.

        :param user_id: int
        :param times: int
        :param position: int
        '''         
        ew = self.session.query(
            Episode_watched,
        ).filter(
            Episode_watched.show_id == self.show_id,
            Episode_watched.episode_number == self.number,
            Episode_watched.user_id == user_id,
        ).first()
        if not ew:
            times = times if times > 0 else 0
            ew = Episode_watched(
                show_id=self.show_id,
                episode_number=self.number,
                user_id=user_id,
                position=position,
                times=times,
            )
            self.session.add(ew)
        else:
            times = ew.times + times            
            times = times if times > 0 else 0
            ew.position = position
            ew.times = times
        return {
            'times': ew.times,
            'position': ew.position,
            'updated_at': ew.updated_at,
        }


class Episode_watched(Base):
    '''Episode watched by the user.'''
    __tablename__ = 'episodes_watched'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    times = sa.Column(sa.Integer, default=0)
    position = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed = sa.Column(utils.YesNoBoolean(), default=False)

    _cache_name = 'users:{}:watched:shows:{}:numbers:{}'
    _cache_name_episodes = 'users:{}:watched:episodes'

    _cache_name_show = 'users:{}:watched:shows:{}'
    _cache_name_show_episodes_watched = 'users:{}:watched:shows:{}:numbers'
    _cache_name_shows_watched = 'users:{}:watched:shows'


    def cache(self):
        '''Sends the user's episode watched info to redis.
        This method is automatically called after update or insert.
        ''' 
        names = (
            self.cache_name,
            self.cache_name_show(
                user_id=self.user_id,
                show_id=self.show_id,
            ),
        )
        for name in names:
            self.session.pipe.hset(name, 'number', self.episode_number)
            self.session.pipe.hset(name, 'times', self.times)
            self.session.pipe.hset(name, 'position', self.position)
            self.session.pipe.hset(name, 'updated_at', utils.isoformat(self.updated_at))    
            self.session.pipe.hset(name, 'completed', self.completed)

        t = get_history(self, 'times')
        if t.added or t.deleted:
            a = t.added[0] if t.added else 0
            d = t.deleted[0] if t.deleted else 0
            self.inc_watched_stats(a-d)

        self.session.pipe.zadd(
            self.cache_name_episodes, 
            self.updated_at.timestamp(), 
            '{}-{}'.format(
                self.show_id,
                self.episode_number,
            )
        )
        self.session.pipe.zadd(
            self.cache_name_show_episodes_watched(
                user_id=self.user_id,
                show_id=self.show_id,
            ), 
            self.updated_at.timestamp(), 
            str(self.episode_number),
        )  
        self.session.pipe.zadd(
            self.cache_name_shows_watched(
                user_id=self.user_id,
            ), 
            self.updated_at.timestamp(), 
            str(self.show_id),
        )

    @property
    def cache_name(self):
        '''
        :returns: str
        '''
        return self._cache_name.format(
            self.user_id, 
            self.show_id, 
            self.episode_number,
        )

    @property
    def cache_name_episodes(self):
        return self._cache_name_episodes.format(
            self.user_id,
        )

    @classmethod
    def cache_name_show_episodes_watched(self, user_id, show_id):
        return self._cache_name_show_episodes_watched.format(
            user_id,
            show_id,
        )
    @classmethod
    def cache_name_shows_watched(self, user_id):
        return self._cache_name_shows_watched.format(
            user_id,
        )
    @classmethod
    def cache_name_show(self, user_id, show_id):
        return self._cache_name_show.format(
            user_id,
            show_id,
        )

    
    def inc_watched_stats(self, times):
        '''Increments the users total episode watched count 
        with `times`. To decrement use negative numbers.

        This method is automatically called when inserting, 
        updating or deleting.

        :param times: int
        :returns: int
        '''
        t = self.session.pipe.hincrby(
            name='users:{}:stats'.format(self.user_id),
            key='episodes_watched',
            amount=times,
        )

    @classmethod
    @auto_session
    @auto_pipe
    def update_minutes_spent(cls, user_id, pipe=None, session=None):
        '''Updates the users total minutes spent.
        Must be called after marking one or more episodes as watched.

        :param user_id: int
        :param pipe: redis pipe
        :param session: sqlalchemy session
        '''
        result = session.execute('''
            SELECT 
                sum(
                    if(isnull(e.runtime),
                        ifnull(s.runtime, 0),
                        e.runtime
                    ) * ew.times
                ) as minutes,
                min(ew.times) as times
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
        result = result.first()
        pipe.hset(
            name='users:{}:stats'.format(user_id),
            key='minutes_spent',
            value=result['minutes'] if result['minutes'] else 0,
        )


    @classmethod
    def get(cls, user_id, show_id, episode_number):
        '''Retrieves watched status for episodes specified by
        the `show_id` and one or more `episode_number`
        from the cache.

        :param user_id: int
        :param show_id: int
        :param episode_number: int or list of int
        :returns: dict or list of dict
            {
                "times": 2,
                "position": 37,
                "updated_at": "2015-02-21T21:11:00Z",
                "completed": True
            }
        '''
        pipe = database.redis.pipeline()
        numbers = episode_number if isinstance(episode_number, list) else \
            [episode_number]
        for n in numbers:            
            pipe.hgetall(cls._cache_name.format(user_id, show_id, n))
        result = pipe.execute()
        watched = []
        for w in result:
            if not w:
                watched.append(None)
                continue
            watched.append({
                'times': int(w['times']),
                'position': int(w['position']),
                'updated_at': w['updated_at'],
                'completed': w['completed'] == 'True',
            })
        return watched if isinstance(episode_number, list) else watched[0]

    def after_upsert(self):
        self.cache()

    def before_upsert(self):
        self.updated_at = datetime.utcnow()
        episode = self
        times_hist = get_history(self, 'times')
        self.completed = True \
            if times_hist.added and times_hist.added[0] > 0 else \
                False

    def after_delete(self):
        names = (
            self.cache_name,
            self.cache_name_show(
                user_id=self.user_id,
                show_id=self.show_id,
            ),
        )
        for name in names:
            self.session.pipe.delete(name)
        self.inc_watched_stats(-self.times)
        self.session.pipe.zrem(
            self.cache_name_episodes, 
            '{}-{}'.format(
                self.show_id,
                self.episode_number,
            )
        )
        self.session.pipe.zrem(
            self.cache_name_show_episodes_watched, 
            str(self.episode_number)
        )        
        self.session.pipe.zrem(
            self.cache_name_shows_watched(
                user_id=self.user_id,
            ),
            str(self.show_id)
        )

    @classmethod
    def show_get(cls, user_id, show_id):
        '''Retrieves the user's watch status from the cache for each 
        show id in `show_id`.

        :param user_id: int
        :param show_id: int or list of int
        :returns: dict or list of dict
            {
                "times": 1,
                "number": 1,
                "position": 37,
                "updated_at": "2015-02-21T21:11:00Z",
                "completed": True
            }
        '''
        pipe = database.redis.pipeline() 
        show_ids = show_id if isinstance(show_id, list) else [show_id]
        for id_ in show_ids:            
            pipe.hgetall(cls.cache_name_show(
                user_id=user_id, 
                show_id=id_,
            ))
        result = pipe.execute()
        watching = []
        for w in result:
            if not w:
                watching.append(None)
                continue
            watching.append({
                'number': int(w['number']),
                'position': int(w['position']),
                'updated_at': w['updated_at'],
                'completed': w['completed'] == 'True',
                'times': int(w['times']),
            })
        return watching if isinstance(show_id, list) else watching[0]


    @classmethod
    def show_recently(cls, user_id, per_page=constants.PER_PAGE, page=1):
        '''Get recently watched shows for a user.

        :returns: `Pagination()`
            `records` will be a list of dict
            [
                {
                    "id": 1,
                    "user_watching": {
                        "times": 1,
                        "number": 1,
                        "position": 37,
                        "updated_at": "2015-02-21T21:11:00Z",
                        "completed": True
                    }
                }
            ]
        '''
        name = cls.cache_name_shows_watched(user_id=user_id)
        start = (page-1)*per_page
        show_ids = database.redis.zrevrange(
            name,   
            start=start,
            end=(start+per_page)-1,
        )
        w = []
        for show_id, watching in zip(show_ids, cls.show_get(user_id, show_ids)):
            w.append({
                'id': int(show_id),
                'user_watching': watching,
            })
        return Pagination(
            page=page,
            per_page=per_page,
            total=database.redis.zcard(name),
            records=w,
        )

@rebuild_cache.register('episodes')
def rebuild_episodes():
    with new_session() as session:
        for item in session.query(Episode).yield_per(10000):
            item.to_elasticsearch()
        session.commit()

@rebuild_cache.register('episode_watched')
def rebuild_episode_watched():
    with new_session() as session:
        for item in session.query(Episode_watched).order_by(
                Episode_watched.updated_at
            ).yield_per(10000):
            item.cache()
        session.commit()