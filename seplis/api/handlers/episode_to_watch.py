from . import base
from seplis.api import exceptions, constants, models
from seplis.api.decorators import authenticated, new_session, run_on_executor
from sqlalchemy import or_, and_

class Handler(base.Handler):

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id):
        episode = await self.episode_to_watch(
            self.current_user.id,
            show_id,
        )
        if not episode:
            self.set_status(204)
        else:
            self.write_object(episode)

    @run_on_executor
    def episode_to_watch(self, user_id, show_id):
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
        with new_session() as session:
            ew = session.query(
                models.Episode_watched.episode_number,
                models.Episode_watched.position,
            ).filter(
                models.Episode_last_finished.user_id == user_id,
                models.Episode_last_finished.series_id == show_id,
                models.Episode_watched.series_id == models.Episode_last_finished.series_id,
                models.Episode_watched.user_id == models.Episode_last_finished.user_id,
                models.Episode_watched.episode_number ==\
                    models.Episode_last_finished.episode_number,
            ).first()

            episode_number = 1
            if ew:
                episode_number = ew.episode_number
                if ew.position == 0:
                    episode_number += 1

            e = session.query(
                models.Episode,
                models.Episode_watched,
            ).filter(
                models.Episode.series_id == show_id,
                models.Episode.number == episode_number,
            ).outerjoin(
                (models.Episode_watched, and_(
                    models.Episode_watched.user_id == user_id,
                    models.Episode_watched.series_id == models.Episode.series_id,
                    models.Episode_watched.episode_number == models.Episode.number,
                ))
            ).first()
            if not e:
               return
            episode = e.Episode.serialize()
            episode['user_watched'] = None
            if e.Episode_watched:
                episode['user_watched'] = e.Episode_watched.serialize()
            return episode