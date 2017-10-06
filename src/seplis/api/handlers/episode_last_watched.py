import logging
from . import base
from seplis.api import models, exceptions, constants
from seplis.api.connections import database
from seplis.api.decorators import authenticated

class Handler(base.Handler):
    """Get the user's latest watched episode for a show.
    The episode must be the latest completed.
    """

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id):
        self.set_status(204)
        ids = database.redis.zrevrange(
            models.Episode_watched.ck_watched_show_episodes(
                self.current_user.id,
                show_id,
            ),
            0, 1
        )
        if not ids:
            return
        watched_list = models.Episode_watched.cache_get(
            self.current_user.id,
            show_id,
            ids,
        )
        watched = watched_list[0]
        episode_number = ids[0]
        
        if watched['position'] > 0:
            if len(watched_list) == 2:
                watched = watched_list[1]
                episode_number = ids[1]
            else:
                return

        episode = await models.Episode.es_get(show_id, episode_number)
        if not episode:
            raise exceptions.Not_found('unknown episode')
        episode['user_watched'] = watched
        self.set_status(200)
        self.write_object(episode)