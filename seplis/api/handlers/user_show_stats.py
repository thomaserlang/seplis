import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants

class Handler(base.Handler):

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id):
        data = await self.query_episodes(show_id)
        self.write_object(data)

    @run_on_executor
    def query_episodes(self, show_id):
        with new_session() as session:
            r = session.query(
                sa.func.sum(models.Episode_watched.times).label('episodes_watched'),
                sa.func.sum(
                    models.Episode_watched.times * \
                        sa.func.ifnull(
                            models.Episode.runtime,
                            models.Series.runtime,
                        )
                ).label('episodes_watched_minutes'),
            ).filter(
                models.Episode_watched.user_id == self.current_user.id,
                models.Episode_watched.show_id == show_id,
                models.Episode.show_id == models.Episode_watched.show_id,
                models.Episode.number == models.Episode_watched.episode_number,
                models.Series.id == models.Episode_watched.show_id,
            ).first()
            d = {
                'episodes_watched': 0,
                'episodes_watched_minutes': 0,
            }
            if not r:
                return d
            d['episodes_watched'] = int(r.episodes_watched) if r.episodes_watched else 0
            d['episodes_watched_minutes'] = int(r.episodes_watched_minutes) if r.episodes_watched_minutes else 0
            return d