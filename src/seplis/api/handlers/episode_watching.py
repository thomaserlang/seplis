import good
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants
from seplis import schemas

class Handler(base.Handler):

    __schema__ = good.Schema({
        'position': good.All(int, good.Range(min=0, max=86400)),
    })

    @authenticated(constants.LEVEL_PROGRESS)
    def get(self, show_id, episode_number):
        w = models.Episode_watched.cache_get(
            user_id=self.current_user.id,
            show_id=show_id,
            episode_number=episode_number,
        )
        if not w:
            self.set_status(204)
        else:
            self.write_object(w)

    @authenticated(constants.LEVEL_PROGRESS)
    async def put(self, show_id, episode_number):
        await self._put(show_id, episode_number)
        self.set_status(204)

    @authenticated(constants.LEVEL_PROGRESS)
    async def delete(self, show_id, episode_number):
        self.request.body = {'position': 0}
        await self._put(show_id, episode_number)
        self.set_status(204)

    @run_on_executor
    def _put(self, show_id, episode_number):
        self.validate(self.__schema__)
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            episode.watched(
                user_id=self.current_user.id,
                times=0,
                position=int(self.request.body['position']),
            )
            session.commit()