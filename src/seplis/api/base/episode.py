import logging
from seplis.decorators import new_session, auto_session
from seplis.connections import database
from seplis.api.base.pagination import Pagination
from seplis.api.base.description import Description
from seplis.api.base.show import Show
from seplis.api import exceptions, constants, models
from seplis import utils
from sqlalchemy import asc
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
    def get(cls, show_id, number, session):
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