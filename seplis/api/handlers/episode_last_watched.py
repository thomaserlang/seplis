import logging
import sqlalchemy as sa
from . import base
from seplis.api import models, exceptions, constants
from seplis.api.connections import database
from seplis.api.decorators import authenticated, new_session, run_on_executor

class Handler(base.Handler):
    """Get the user's latest watched episode for a show.
    The episode must be the latest completed.
    """

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id):
        episode = await self.get_episode(show_id)
        if not episode:
            self.set_status(204)
        else:
            self.write_object(episode)

    @run_on_executor
    def get_episode(self, show_id):
        with new_session() as session:
            eps = session.query(
                models.Episode,
                models.Episode_watched,
            ).filter(
                models.Episode_watched.user_id == self.current_user.id,
                models.Episode_watched.series_id == show_id,
                models.Episode.series_id == models.Episode_watched.series_id,
                models.Episode.number == models.Episode_watched.episode_number,
            ).order_by(
                sa.desc(models.Episode_watched.watched_at),
                sa.desc(models.Episode_watched.episode_number),
            ).limit(2).all()
            if not eps:
                return
                
            e = eps[0]
            if len(eps) == 1:
                if eps[0].Episode_watched.position > 0:
                    return
            else:
                if eps[0].Episode_watched.position > 0:
                    e = eps[1]

            episode = e.Episode.serialize()
            episode['user_watched'] = e.Episode_watched.serialize()
            return episode