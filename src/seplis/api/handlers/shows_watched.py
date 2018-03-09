import logging
from sqlalchemy import desc
from . import base
from seplis import schemas, utils
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api.connections import database

class Handler(base.Pagination_handler):

    async def get(self, user_id):
        user_id = self.user_id_or_current(user_id) 
        super().get()
        r = await self.get_shows(user_id)
        self.write_object(r)

    @run_on_executor
    def get_shows(self, user_id):
        with new_session() as session:
            elw = models.Episode_watching
            ew = models.Episode_watched
            p = session.query(
                models.Show,
                models.Episode_watched,
                models.Episode,
            ).filter(
                elw.user_id == user_id,
                ew.user_id == elw.user_id,
                ew.show_id == elw.show_id,
                ew.episode_number == elw.episode_number,            
                models.Show.id == elw.show_id,
                models.Episode.show_id == elw.show_id,
                models.Episode.number == elw.episode_number,
            ).order_by(
                desc(ew.watched_at), desc(elw.show_id)
            ).paginate(self.page, self.per_page)

            records = []
            for r in p.records:
                d = r.Show.serialize()
                d['user_watching'] = r.Episode_watched.serialize()
                d['user_watching']['episode'] = r.Episode.serialize()
                records.append(d)
            p.records = records
            return p
