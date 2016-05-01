from . import base
from seplis.api import components, exceptions, constants
from seplis.api.decorators import authenticated

class Handler(base.Handler):

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id):
        episode = await components.show.episode_to_watch(
            self.current_user.id,
            show_id,
        )
        if not episode:
            raise exceptions.User_no_episode_to_watch()
        self.write_object(episode)