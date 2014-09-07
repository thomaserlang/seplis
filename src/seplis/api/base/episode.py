import logging
from seplis.decorators import new_session
from seplis.connections import database
from seplis.api.base.pagination import Pagination
from seplis.api.base.description import Description
from seplis.api import exceptions, constants, models
from seplis import utils
from sqlalchemy import asc

class Episode(object):

    def __init__(self, number, title=None, air_date=None, 
                 description=None, season=None, episode=None):
        '''

        :param title: str
        :param number: int
        :param air_date: `datetime.date()`
        :param description: `seplis.api.base.description.Description()`
        :param season: int
        :param episode: int
        '''
        self.number = number
        self.title = title
        self.air_date = air_date
        self.description = description
        self.season = season
        self.episode = episode

    def to_dict(self):
        return self.__dict__

    def save(self, show_id, session=None):
        '''

        :param show_id: int
        :param session: SQLAlchemy session
        :returns: boolean
        '''
        if not session:
            with new_session() as session:
                self._save(show_id, session)
                session.commit()
                return True
        else:
            self._save(show_id, session)
            return True

    def _save(self, show_id, session):
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
        )

    @classmethod
    def get(cls, show_id, number, session=None):
        if not session:
            with new_session() as session:
                return cls._get(show_id, number, session)
        return cls._get(show_id, number, session)

    @classmethod
    def _get(cls, show_id, number, session):
        episode = session.query(
            models.Episode,
        ).filter(
            models.Episode.show_id == show_id,
            models.Episode.number == number,
        ).first()
        if not episode:
            return None
        return cls._format_from_row(
            episode
        )



class Episodes(object):

    @classmethod
    def save(cls, show_id, episodes, session=None):        
        '''
        Save a list of episodes.

        :param show_id: int
        :param episodes: [`Episode()`]
        :returns boolean
        '''
        if not session:
            with new_session() as session:
                cls._save(show_id, episodes, session)
                session.commit()
                return True
        else:
            return cls._save(show_id, episodes, session)

    @classmethod
    def _save(cls, show_id, episodes, session):
        for episode in episodes:
            episode.save(show_id, session)
        return True

    @classmethod
    def get(cls, show_id, from_, to, loop_prevent=False):
        key = 'shows:{}:episodes'.format(show_id)
        episodes_ids = database.redis.zrange(
            name=key,
            start=from_ - 1,
            end=to - 1,
        )
        if utils.not_redis_none(episodes_ids):
            episode_ids = [
                'episodes:{}'.format(id_) 
                for id_ in episodes_ids
            ]
            episodes = []
            if episode_ids:
                episodes = [
                    utils.json_loads(episode) 
                    for episode in database.redis.mget(episode_ids)
                    if episode
                ]
            return episodes
        if database.redis.exists(key) or loop_prevent:
            return None
        # no episodes was found, gotta "cache" 'em all and run it again!
        cls.recache(show_id)        
        return cls.get(show_id, from_, to, True)


    @classmethod
    def recache(cls, show_id):
        with new_session() as session:
            episodes = session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id==show_id,
            ).order_by(
                asc(models.Episode.number),
            ).all()
            if not episodes:
                database.redis.set(key, None)
                return None
            with database.redis.pipeline() as pipe:
                for episode in episodes:
                    Episode.cache(
                        pipe=pipe, 
                        show_id=show_id, 
                        number=episode.number, 
                        data=episode.data,
                    )
                    Episode.to_elasticsearch(
                        show_id, 
                        episode.number,
                        episode.data,
                    )
                pipe.execute()