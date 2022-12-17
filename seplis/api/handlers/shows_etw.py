import logging
from sqlalchemy import func, or_, desc
from . import base
from seplis.api import constants, exceptions, models
from seplis.api.decorators import run_on_executor, new_session
from datetime import datetime, timedelta

class Handler(base.Pagination_handler):

    async def get(self, user_id):
        user_id = self.user_id_or_current(user_id) 
        super().get()
        shows = await self.shows(user_id)
        self.write_object(shows)

    @run_on_executor
    def shows(self, user_id):
        with new_session() as session:
            now_ = datetime.utcnow()
            episodes = session.query(
                models.Episode_watched.series_id.label('show_id'),
                func.max(models.Episode_watched.episode_number).label('episode_number'),
            ).filter(
                models.Episode_watched.user_id == user_id,
                models.Series_follower.user_id == models.Episode_watched.user_id,
                models.Series_follower.series_id == models.Episode_watched.series_id,
                models.Episode_watched.times > 0,
            ).group_by(models.Episode_watched.series_id).subquery()

            p = session.query(models.Series, models.Episode).filter(
                models.Series.id == episodes.c.show_id,
                models.Episode.series_id == models.Series.id,
                models.Episode.number == episodes.c.episode_number+1,
                models.Episode.air_datetime <= now_,
            ).order_by(
                desc(models.Episode.air_datetime),
                models.Episode.series_id,
            ).paginate(page=self.page, per_page=self.per_page)
            p.records = [{
                'show': r.Show.serialize(), 
                'episode': r.Episode.serialize()
            } for r in p.records]
            return p