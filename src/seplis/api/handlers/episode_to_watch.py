from . import base
from seplis.api import exceptions, constants, models
from seplis.api.decorators import authenticated

class Handler(base.Handler):

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id):
        episode = await self.episode_to_watch(
            self.current_user.id,
            show_id,
        )
        if not episode:
            raise exceptions.User_no_episode_to_watch()
        self.write_object(episode)

    async def episode_to_watch(self, user_id, show_id):
        """Returns which episode to watch for a show.

        * Return episode 1 if the user has not watched any episodes.
        * If the user is watching an episode and it is not completed 
          return that one.
        * If the latest episode watched by the user is completed
          return the latest + 1.

        If the next episode does not exist or the show has no
        episodes the result will be `None`.

        :returns: episode dict with "user_watched" field.
            {
                "number": 1,
                "title": "asd",
                "user_watched": {
                    "times": 1,
                    "position": 100,
                }
            }

        """
        watching = models.Episode_watched.show_get(
            user_id=user_id, 
            show_id=show_id,
        )
        number = 1
        if watching:
            if watching['completed']:
                number = watching['episode_number'] + 1
            else:
                number = watching['episode_number']
        episode = await models.Episode.es_get(show_id, number)
        if not episode:
            return
        episode['user_watched'] = models.Episode_watched.get(
            user_id=user_id,
            show_id=show_id,
            episode_number=number,
        )
        return episode