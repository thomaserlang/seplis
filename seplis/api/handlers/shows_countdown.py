import logging
from sqlalchemy import func
from . import base
from seplis.api import constants, exceptions, models
from seplis.api.decorators import run_on_executor, new_session
from datetime import datetime

class Handler(base.Pagination_handler):

    async def get(self, user_id):
        user_id = self.user_id_or_current(user_id) 
        super().get()
        shows = await self.shows(user_id)
        self.write_object(shows)

    @run_on_executor
    def shows(self, user_id):
        with new_session() as session:
            episodes = session.query(
                models.Episode.show_id.label('show_id'),
                func.min(models.Episode.number).label('episode_number'),
            ).filter(
                models.Series_following.user_id == user_id,
                models.Episode.show_id == models.Series_following.show_id,
                models.Episode.air_datetime > datetime.utcnow(),
            ).group_by(models.Episode.show_id).subquery()
            p = session.query(models.Series, models.Episode).filter(
                models.Series.id == episodes.c.show_id,
                models.Episode.show_id == models.Series.id,
                models.Episode.number == episodes.c.episode_number,
            ).order_by(
                models.Episode.air_datetime,
                models.Episode.show_id,
            ).paginate(page=self.page, per_page=self.per_page)
            p.records = [{
                'show': r.Show.serialize(), 
                'episode': r.Episode.serialize()
            } for r in p.records]
            return p