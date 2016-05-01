from . import base
from seplis.api import components, exceptions

class Handler(base.Handler):

    async def get(self, user_id, show_id):
        episode = await components.show.episode_to_watch(
            user_id,
            show_id,
        )
        if not episode:
            raise exceptions.User_no_episode_to_watch()
        self.write_object(episode)