from seplis.api import models
from seplis.api.connections import database

async def append_user_watching(user_id, shows):
    """Appends the "user_watching" field to each show in `shows`.

    The "user_watching" field contains the latest episode watch data
    for the user.

        ```
        show = {
            "id": 1,
            "user_watching": {
                "times": 1,
                "number": 1,
                "position": 37,
                "updated_at": "2015-02-21T21:11:00Z",
                "completed": False,
                "episode": { ... }
            }
        }
        ```
    """
    if not shows:
        return
    show_ids = [show['id'] for show in shows]
    watching = models.Episode_watched.show_get(
        user_id=user_id, 
        show_id=show_ids
    )
    episode_ids = ['{}-{}'.format(show_id, w['episode_number'] if w else 0)
        for show_id, w in zip(show_ids, watching)]
    result = await database.es_get('/episodes/episode/_mget', body={
        'ids': episode_ids
    })
    episodes = [d.get('_source') for d in result['docs']]
    for w, episode, show in zip(watching, episodes, shows):
        if w:
            w['episode'] = episode
        show['user_watching'] = w