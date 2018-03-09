import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants

class Handler(base.Handler):

    async def get(self, user_id):
        user_id = self.user_id_or_current(user_id)
        fan_of = await self.query_fan_of(user_id)
        episodes = await self.query_episodes(user_id)
        shows_watched = await self.query_shows_watched(user_id)
        data = fan_of
        data.update(episodes)
        data.update(shows_watched)
        self.write_object(data)

    @run_on_executor
    def query_fan_of(self, user_id):
        with new_session() as session:
            r = session.query(
                sa.func.count(models.Show_fan.show_id).label('user_fan_of'),
            ).filter(
                models.Show_fan.user_id == user_id,
            ).first()
            if not r:
                return {'fan_of': 0}
            return {
                'fan_of': r.user_fan_of or 0,
            }

    @run_on_executor
    def query_shows_watched(self, user_id):
        with new_session() as session:
            r = session.query(
                sa.func.count(sa.func.distinct(
                    models.Episode_watched.show_id
                )).label('shows_watched'),
            ).filter(
                models.Episode_watched.user_id == user_id,
            ).first()
            if not r:
                return {'shows_watched': 0}
            return {
                'shows_watched': r.shows_watched or 0,
            }

    @run_on_executor
    def query_episodes(self, user_id):
        with new_session() as session:
            r = session.query(
                sa.func.sum(models.Episode_watched.times).label('episodes_watched'),
                sa.func.sum(
                    models.Episode_watched.times * \
                        sa.func.ifnull(
                            models.Episode.runtime,
                            models.Show.runtime,
                        )
                ).label('episodes_watched_minutes'),
            ).filter(
                models.Episode_watched.user_id == user_id,
                models.Episode.show_id == models.Episode_watched.show_id,
                models.Episode.number == models.Episode_watched.episode_number,
                models.Show.id == models.Episode_watched.show_id,
            ).first()
            d = {
                'episodes_watched': 0,
                'episodes_watched_minutes': 0,
            }
            if not r:
                return d
            d['episodes_watched'] = int(r.episodes_watched) if r.episodes_watched else 0
            d['episodes_watched_minutes'] = int(r.episodes_watched_minutes) if r.episodes_watched else 0
            return d