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
from datetime import datetime, time

class Episode(Base):
    __tablename__ = 'episodes'

    show_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(200), unique=True)
    air_date = sa.Column(sa.Date)
    air_time = sa.Column(sa.Time)
    air_datetime = sa.Column(sa.DateTime)
    description_text = sa.Column(sa.Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    season = sa.Column(sa.Integer)
    episode = sa.Column(sa.Integer)
    runtime = sa.Column(sa.Integer)

    def serialize(self):
        return  {
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
            'air_time': self.air_time,
            'air_datetime': self.air_datetime,
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
        self.session.es_bulk.append({
            '_op_type': 'delete',
            '_index': 'episodes',
            '_type': 'episode',
            '_id': '{}-{}'.format(self.show_id, self.number),
        })

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
    """Episode watched by the user."""
    __tablename__ = 'episodes_watched'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    times = sa.Column(sa.Integer, default=0)
    position = sa.Column(sa.Integer, default=0)
    watched_at = sa.Column(sa.DateTime)

    def serialize(self):
        return utils.row_to_dict(self)

    def set_as_watching(self):
        lew = Episode_watching(
            show_id=self.show_id,
            episode_number=self.episode_number,
            user_id=self.user_id,
        )
        self.session.merge(lew)

    def set_prev_as_watching(self):
        lew = self.session.query(Episode_watching).filter(
            Episode_watching.show_id == self.show_id,
            Episode_watching.user_id == self.user_id,
        ).first()
        if not lew or lew.episode_number != self.episode_number:
            return
        ep = self.session.query(Episode_watched).filter(
            Episode_watched.user_id == self.user_id,
            Episode_watched.show_id == self.show_id,
            Episode_watched.episode_number != self.episode_number,
        ).order_by(
            sa.desc(Episode_watched.episode_number),
        ).first()
        if ep:
            ep.set_as_watching()
        else:
            self.session.query(Episode_watching).filter(
                Episode_watching.user_id == self.user_id,
                Episode_watching.show_id == self.show_id,
            ).delete()

class Episode_watching(Base):
    __tablename__ = 'episode_watching'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    episode_number = sa.Column(sa.Integer)

@rebuild_cache.register('episodes')
def rebuild_episodes():
    with new_session() as session:
        for item in session.query(Episode).yield_per(10000):
            item.to_elasticsearch()
        session.commit()