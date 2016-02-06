import good
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session
from seplis.api import models, exceptions, constants
from seplis import schemas
from tornado import gen, web
from tornado.concurrent import run_on_executor

class Handler(base.Handler):

    validation_schema = good.Schema({
        'position': good.All(int, good.Range(min=0, max=86400)),
    })

    @authenticated(constants.LEVEL_PROGRESS)
    @gen.coroutine
    def put(self, user_id, show_id, episode_number):
        yield self._put(user_id, show_id, episode_number)

    @run_on_executor
    def _put(self, user_id, show_id, episode_number):
        self.validate(self.validation_schema)
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            episode.watched(
                user_id=user_id,
                times=0,
                position=int(self.request.body['position']),
            )
            session.commit()


    @authenticated(constants.LEVEL_PROGRESS)
    def get(self, user_id, show_id, episode_number):
        w = models.Episode_watched.get(
            user_id=user_id,
            show_id=show_id,
            episode_number=episode_number,
        )
        if not w:
            raise exceptions.Not_found('the user has not watched this episode')
        self.write_object(w)