import seplis.api.handlers.episode
from seplis.api.handlers import base
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated
from seplis import schemas, utils
from tornado import gen, web
from tornado.concurrent import run_on_executor

class Handler(base.Handler):

    @gen.coroutine
    def get(self, user_id, show_id):
        episode_number = self.get_next_episode_number(
            user_id,
            show_id,
        )
        self.append_fields = self.get_append_fields(
            seplis.api.handlers.episode.Handler.allowed_append_fields
        )
        yield \
            seplis.api.handlers.episode.Handler.get_episode(
                self,
                show_id=show_id,
                number=episode_number,
            )

    def get_next_episode_number(self, user_id, show_id):
        rw = models.Episode_watched.recently(
            user_id=user_id,
            show_id=show_id,
            per_page=1,
        )
        if rw.total == 0:
            return 1
        epnum = rw.records[0]['episode_number']
        ew = models.Episode_watched.get(
            user_id=user_id,
            show_id=show_id,
            episode_number=epnum,
        )
        if not ew['completed']:
            return epnum
        else:
            return epnum + 1
