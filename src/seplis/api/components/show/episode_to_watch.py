from seplis.api import models
from seplis.api.connections import database

async def episode_to_watch(user_id, show_id):
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
            number = watching['number'] + 1
        else:
            number = watching['number']
    episode_response = await database.es_get('/episodes/episode/{}-{}'.format(
        show_id,
        number,
    ))
    if not episode_response['found']:
        return
    episode = episode_response['_source']
    episode['user_watched'] = models.Episode_watched.get(
        user_id=user_id,
        show_id=show_id,
        episode_number=number,
    )
    return episode