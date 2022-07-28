import good
from datetime import datetime
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants
from seplis import schemas

class Handler(base.Handler):

    __schema__ = good.Schema({
        'position': good.All(int, good.Range(min=0, max=86400)),
    })

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id, episode_number):
        w = await self._get(show_id, episode_number)
        if not w:
            self.set_status(204)
        else:
            self.write_object(w)

    @run_on_executor
    def _get(self, show_id, episode_number):
        with new_session() as session:
            r = session.query(models.Episode_watched).filter(
                models.Episode_watched.show_id == show_id,
                models.Episode_watched.episode_number == episode_number,
            ).first()
            if r:
                return r.serialize()            

    @authenticated(constants.LEVEL_PROGRESS)
    async def put(self, show_id, episode_number):
        await self._put(show_id, episode_number)
        self.set_status(204)

    @authenticated(constants.LEVEL_PROGRESS)
    async def delete(self, show_id, episode_number):
        self.request.body = {'position': 0}
        await self.reset_position(show_id, episode_number)
        self.set_status(204)

    @run_on_executor
    def _put(self, show_id, episode_number):
        data = self.validate(self.__schema__)
        with new_session() as session:            
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()

            ew = session.query(models.Episode_watched).filter(
                models.Episode_watched.show_id == show_id,
                models.Episode_watched.episode_number == episode_number,
                models.Episode_watched.user_id == self.current_user.id,
            ).first()
            if not ew:
                ew = models.Episode_watched(
                    show_id=show_id,
                    episode_number=episode_number,
                    user_id=self.current_user.id,
                )
                session.add(ew)
            ew.position = data['position']
            if ew.position > 0:
                ew.watched_at = datetime.utcnow()
                ew.set_as_watching()
            else:
                ew.set_prev_as_watching()
                if ew.times == 0 and ew.position == 0:
                    session.delete(ew)
            session.commit()

    @run_on_executor
    def reset_position(self, show_id, episode_number):
        with new_session() as session:
            ew = session.query(models.Episode_watched).filter(
                models.Episode_watched.show_id == show_id,
                models.Episode_watched.episode_number == episode_number,
                models.Episode_watched.user_id == self.current_user.id,
            ).first()
            if ew:
                ew.position = 0
                if ew.times == 0:
                    ew.set_prev_as_watching()
                    session.delete(ew)
                session.commit()