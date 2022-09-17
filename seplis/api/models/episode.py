import logging
import elasticsearch
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

    @property
    def description(self):
        return {
            'text': self.description_text,
            'title': self.description_title,
            'url': self.description_url,
        }


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