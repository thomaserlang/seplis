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

    @staticmethod
    async def es_get(show_id, number):
        """Retrives an episode from ES.
        See `Episode.serialize()` for the return format.
        """
        response = await database.es_get(
            '/episodes/episode/{}-{}'.format(
                show_id,
                number,
            )
        )
        if not response['found']:
            return
        response['_source'].pop('show_id')
        return response['_source']

    @staticmethod
    async def es_get_multi(show_id, numbers):
        """Retrives episodes from ES.
        Returns a list of a serialized episode.
        See `Episode.serialize()` for the return format.
        """
        ids = ['{}-{}'.format(show_id, number) for number in numbers]
        result = await database.es_get('/episodes/episode/_mget', body={
            'ids': ids
        })
        episodes = []
        for episode in result['docs']:
            if '_source'in episode:
                episode['_source'].pop('show_id')
                episodes.append(episode['_source'])
            else:
                episodes.append(None)                
        return episodes

class Episode_watched(Base):
    """Episode watched by the user.

    Cached data:

    Episode watched data: 
        Use `cache_get(user_id, show_id, episode_number)`

    Show latest watched:
        Use: `cache_get_show(user_id, show_id)`

    Watched shows:
        A sorted Redis set with the timestamp of the latest
        episode as the score value.
        Use `ck_watched_shows(user_id)` to generate the key.

    Watched show episodes:
        A sorted Redis set with the timestamp of when
        the episode was watched as the score value.
        Use `ck_watched_show_episodes(user_id, show_id)` to generate the key.

    """
    __tablename__ = 'episodes_watched'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    times = sa.Column(sa.Integer, default=0)
    position = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed = sa.Column(utils.YesNoBoolean(), default=False)

    def after_upsert(self):
        self.cache()

    def before_upsert(self):
        self.updated_at = datetime.utcnow()
        times_hist = get_history(self, 'times')
        self.completed = True \
            if times_hist.added and times_hist.added[0] > 0 else \
                False

    def after_delete(self):
        self.cr_data()
        self.cr_latest_data()
        self.cr_watched_shows()
        self.cr_watched_show_episodes()

        self.inc_watched_stats(-self.times)

    @staticmethod
    def ck_data(user_id, show_id, episode_number):
        return 'users:{}:watched:shows:{}:episodes:{}'.format(
            user_id,
            show_id,
            episode_number,
        )
    def cs_data(self):
        """Saves the episode's watched data to the cache as a hset."""
        key = self.ck_data(self.user_id, self.show_id, self.episode_number)
        hset = self.session.pipe.hset
        hset(key, 'times', self.times)
        hset(key, 'position', self.position)
        hset(key, 'updated_at', utils.isoformat(self.updated_at))    
        hset(key, 'completed', self.completed)
    def cr_data(self):
        self.session.pipe.delete(
            self.ck_data(self.user_id, self.show_id, self.episode_number)
        )

    @staticmethod
    def ck_latest_data(user_id, show_id):
        """Cache key for the latest episode watched data
        for a show.
        See `cs_latest_data` for how data is stored.
        """
        return 'users:{}:watched:shows:{}'.format(
            user_id,
            show_id,
        )
    def cs_latest_data(self):
        key = self.ck_latest_data(self.user_id, self.show_id)
        hset = self.session.pipe.hset
        hset(key, 'episode_number', self.episode_number)
        hset(key, 'times', self.times)
        hset(key, 'position', self.position)
        hset(key, 'updated_at', utils.isoformat(self.updated_at))    
        hset(key, 'completed', self.completed)
    def cr_latest_data(self):
        self.session.pipe.delete(
            self.ck_latest_data(self.user_id, self.show_id)
        )

    @staticmethod
    def ck_watched_show_episodes(user_id, show_id):
        return 'users:{}:watched:shows:{}:episodes'.format(
            user_id,
            show_id,
        )
    def cs_watched_show_episodes(self):
        key = self.ck_watched_show_episodes(
            user_id=self.user_id,
            show_id=self.show_id,
        )
        self.session.pipe.zadd(
            key, 
            self.updated_at.timestamp(), 
            str(self.episode_number),
        )
    def cr_watched_show_episodes(self):
        key = self.ck_watched_show_episodes(
            user_id=self.user_id,
            show_id=self.show_id,
        )
        self.session.pipe.zrem(
            key,
            str(self.episode_number)
        )

    @staticmethod
    def ck_watched_shows(user_id):
        return 'users:{}:watched:shows'.format(
            user_id,
        )
    def cs_watched_shows(self):
        key = self.ck_watched_shows(self.user_id)
        self.session.pipe.zadd(
            key, 
            self.updated_at.timestamp(), 
            str(self.show_id),
        )
    def cr_watched_shows(self):
        key = self.ck_watched_shows(
            user_id=self.user_id,
        )
        self.session.pipe.zrem(
            key,
            str(self.show_id)
        )

    def cache(self):
        """Sends the user's episode watched info to redis.
        This method is automatically called after update or insert.
        """ 
        self.cs_data()
        self.cs_latest_data()
        self.cs_watched_show_episodes()
        self.cs_watched_shows()

        t = get_history(self, 'times')
        if t.added or t.deleted:
            a = t.added[0] if t.added else 0
            d = t.deleted[0] if t.deleted else 0
            self.inc_watched_stats(a-d)
    
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
    def cache_get(cls, user_id, show_id, episode_number):
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
            pipe.hgetall(cls.ck_data(user_id, show_id, n))
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

    @classmethod
    def cache_get_show(cls, user_id, show_id):
        '''Retrieves the user's watch status from the cache for each 
        show id in `show_id`.

        :param user_id: int
        :param show_id: int or list of int
        :returns: dict or list of dict
            {
                "times": 1,
                "episode_number": 1,
                "position": 37,
                "updated_at": "2015-02-21T21:11:00Z",
                "completed": True
            }
        '''
        pipe = database.redis.pipeline() 
        show_ids = show_id if isinstance(show_id, list) else [show_id]
        for id_ in show_ids:            
            pipe.hgetall(cls.ck_latest_data(
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
                'episode_number': int(w['episode_number']),
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
                        "episode_number": 1,
                        "times": 1,
                        "position": 37,
                        "updated_at": "2015-02-21T21:11:00Z",
                        "completed": True
                    }
                }
            ]
        '''
        name = cls.ck_watched_shows(user_id=user_id)
        start = (page-1)*per_page
        show_ids = database.redis.zrevrange(
            name,   
            start=start,
            end=(start+per_page)-1,
        )
        w = []
        for show_id, watching in zip(show_ids, cls.cache_get_show(user_id, show_ids)):
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