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
        session = orm.Session.object_session(self)
        session.es_bulk.append({
            '_index': 'episodes',
            '_type': 'episode',
            '_id': '{}-{}'.format(self.show_id, self.number),
            '_source': utils.json_dumps(self.serialize()),
        })

    def after_upsert(self):
        self.to_elasticsearch()

    def unwatch(self, user_id):
        '''Removes this episode from the user's watched list.

        :param user_id: int
        '''
        session = orm.Session.object_session(self)
        w = session.query(
            Episode_watched,
        ).filter(
            Episode_watched.show_id == self.show_id,
            Episode_watched.episode_number == self.number,
            Episode_watched.user_id == user_id,
        ).first()
        if not w:
            raise exceptions.User_episode_not_watched()
        session.delete(w)

    def watched(self, user_id, times=1, position=0):
        '''Marks the episode as watched for the user.

        :param user_id: int
        :param times: int
        :param position: int
        '''   
        session = orm.Session.object_session(self)        
        ew = session.query(
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
            session.add(ew)
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

    _cache_name = 'users:{}:watched:shows:{}:numbers:{}'

    def cache(self):
        '''Sends the user's episode watched info to redis.
        This method is automatically called after update or insert.
        ''' 
        session = orm.Session.object_session(self)
        name = self.cache_name
        session.pipe.hset(name, 'times', self.times)
        session.pipe.hset(name, 'position', self.position)
        session.pipe.hset(name, 'updated_at', utils.isoformat(self.updated_at))
        t = get_history(self, 'times')
        if t.added or t.deleted:
            a = t.added[0] if t.added else 0
            d = t.deleted[0] if t.deleted else 0
            self.inc_watched_stats(a-d)

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

    def inc_watched_stats(self, times):
        '''Increments the users total episode watched count 
        with `times`. To decrement use negative numbers.

        This method is automatically called when inserting, 
        updating or deleting.

        :param times: int
        :returns: int
        '''
        session = orm.Session.object_session(self)
        t = session.pipe.hincrby(
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
        '''Retrives episodes watched by the user for a show
        from the cache.

        :param user_id: int
        :param show_id: int
        :param episode_number: int or list of int
        :returns: dict or list of dict
            {
                "times": 2,
                "position": 37,
                "updated_at": "2015-02-21T21:11:00Z"
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
            })
        return watched if isinstance(episode_number, list) else watched[0]

    def after_upsert(self):
        self.cache()

    def before_upsert(self):
        self.updated_at = datetime.utcnow()
        Show_watched.set_watching(
            self.session,
            show_id=self.show_id,
            user_id=self.user_id,
            episode_watched=self,
        )

    def after_delete(self):
        Show_watched.set_watching(
            self.session,
            show_id=self.show_id,
            user_id=self.user_id,
            episode_watched=self.session.query(Episode_watched).filter(
                Episode_watched.show_id == self.show_id,
                Episode_watched.user_id == self.user_id,
            ).order_by(
                sa.desc(Episode_watched.updated_at)
            ).first(),
        )
        self.session.pipe.delete(self.cache_name)
        self.inc_watched_stats(-self.times)

class Show_watched(Base):
    '''Latest episode watched for a user per show.'''
    __tablename__ = 'shows_watched'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, autoincrement=False)
    position = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.DateTime)

    _cache_name = 'users:{}:watched:shows:{}'
    _cache_name_set = 'users:{}:watched:shows'

    def cache(self):
        name = self.cache_name
        self.session.pipe.hset(name, 'number', self.episode_number) 
        self.session.pipe.hset(name, 'position', self.position)
        self.session.pipe.hset(name, 'updated_at', utils.isoformat(self.updated_at))
        self.session.pipe.zadd(
            self.cache_name_set, 
            self.updated_at.timestamp(), self.show_id            
        )

    @property    
    def cache_name(self):
        return self._cache_name.format(
            self.user_id, 
            self.show_id
        )
    @property
    def cache_name_set(self):
        return self._cache_name_set.format(
            self.user_id,
        )

    def after_upsert(self):
        self.cache()

    def after_delete(self):
        self.session.pipe.delete(self.cache_name)
        self.session.pipe.delete(self.cache_name_set, str(self.show_id))

    @classmethod
    def set_watching(cls, session, show_id, user_id, episode_watched):
        ''' Sets an episode as the latest watched for a show
        by the user. If `episode` is None the entry will be deleted.

        Called by `Episode_watched` after update or delete.
        '''
        sw = session.query(
            Show_watched,
        ).filter(
            Show_watched.show_id == show_id,
            Show_watched.user_id == user_id,
        ).first()
        if not episode_watched:
            if sw:
                session.delete(sw)
            return
        if not sw:
            sw = cls(                    
                show_id=episode_watched.show_id,
                episode_number=episode_watched.episode_number,
                user_id=episode_watched.user_id,                    
                position=episode_watched.position,
                updated_at=episode_watched.updated_at,
            )                
            session.add(sw)
        else:
            sw.episode_number = episode_watched.episode_number
            sw.position = episode_watched.position
            sw.updated_at = episode_watched.updated_at

    @classmethod
    def get(cls, user_id, show_id):
        '''Retrives the users watch status from the cache for each 
        show id in `show_id`.

        :param user_id: int
        :param show_id: int or list of int
        :returns: dict or list of dict
            {
                "number": 1,
                "position": 37,
                "updated_at": "2015-02-21T21:11:00Z"
            }
        '''
        pipe = database.redis.pipeline() 
        show_ids = show_id if isinstance(show_id, list) else [show_id]
        for id_ in show_ids:            
            pipe.hgetall(cls._cache_name.format(user_id, id_))
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
            })
        return watching if isinstance(show_id, list) else watching[0]

    @classmethod
    def recently(cls, user_id, per_page=constants.PER_PAGE, page=1):
        '''Get recently watched shows for a user.

        :returns: `Pagination()`
            `records` will be a list of dict
            [
                {
                    "id": 1,
                    "user_watching": {
                        "number": 1,
                        "position": 37,
                        "updated_at": "2015-02-21T21:11:00Z"
                    }
                }
            ]
        '''
        name = cls._cache_name_set.format(user_id)
        start = (page-1)*per_page
        show_ids = database.redis.zrevrange(
            name,   
            start=start,
            end=(start+per_page)-1,
        )
        w = []
        for show_id, watching in zip(show_ids, cls.get(user_id, show_ids)):
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
        for item in session.query(Episode_watched).yield_per(10000):
            item.cache()
        session.commit()

@rebuild_cache.register('show_watched')
def rebuild_show_watched():
    with new_session() as session:
        user_ids = []
        for item in session.query(Show_watched).yield_per(10000):
            item.cache()
            user_ids.append(item.user_id)
        for id_ in set(user_ids):
            Episode_watched.update_minutes_spent
        session.commit()