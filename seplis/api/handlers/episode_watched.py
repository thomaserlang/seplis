import logging
import good
from datetime import datetime
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants
from tornado import gen, web
from sqlalchemy import asc

class Handler(base.Handler):

    __schema__ = good.Schema({
        'times': good.All(
            int, 
            good.Range(min=-20, max=20)
        ),
    }, default_keys=good.Optional)


    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, show_id, episode_number):
        w = await self._get(
            show_id=show_id,
            episode_number=episode_number,
        )
        if w:
            self.write_object(w)
        else:
            self.set_status(204)

    @authenticated(constants.LEVEL_PROGRESS)
    async def put(self, show_id, episode_number):
        w = await self._put(show_id, episode_number)
        if w:
            self.write_object(w)
        else:
            self.set_status(204)

    @authenticated(0)
    async def delete(self, show_id, episode_number):
        await self._delete(show_id, episode_number)
        self.set_status(204)

    @run_on_executor
    def _get(self, show_id, episode_number):
        with new_session() as session:
            ew = session.query(models.Episode_watched).filter(
                models.Episode_watched.series_id == show_id,
                models.Episode_watched.episode_number == episode_number,
                models.Episode_watched.user_id == self.current_user.id,
            ).first()
            if ew:
                return ew.serialize()

    @run_on_executor
    def _put(self, show_id, episode_number):
        data = self.validate()
        with new_session() as session:
            ew = set_watched(
                session=session,
                user_id=self.current_user.id,
                show_id=show_id,
                episode_number=episode_number,
                times=data.get('times', 1),
            )
            session.commit()
            if ew:
                return ew.serialize()

    @run_on_executor
    def _delete(self, show_id, episode_number):
        with new_session() as session:
            ew = session.query(models.Episode_watched).filter(
                models.Episode_watched.series_id == show_id,
                models.Episode_watched.episode_number == episode_number,
                models.Episode_watched.user_id == self.current_user.id,
            ).first()
            if ew:
                ew.set_prev_as_watching()
                session.delete(ew)
            session.commit()

def set_watched(session, user_id, show_id, episode_number, times):
    episode = session.query(models.Episode).filter(
        models.Episode.series_id == show_id,
        models.Episode.number == episode_number,
    ).first()
    if not episode:
        raise exceptions.Episode_unknown()

    ew = session.query(models.Episode_watched).filter(
        models.Episode_watched.series_id == show_id,
        models.Episode_watched.episode_number == episode_number,
        models.Episode_watched.user_id == user_id,
    ).first()

    if not ew:
        ew = models.Episode_watched(
            show_id=show_id,
            episode_number=episode_number,
            user_id=user_id,
            times=0,
        )
        session.add(ew)

    if ew.times < ew.times+times:
        ew.watched_at = datetime.utcnow()
        ew.set_as_watching()

    ew.times += times
    ew.position = 0
    
    if ew.times <= 0:
        ew.set_prev_as_watching()
        session.delete(ew)
        return None
    return ew

class Range_handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    async def put(self, show_id, from_, to):
        await self._put(show_id, int(from_), int(to))
        self.set_status(204)

    @run_on_executor
    def _put(self, show_id, from_, to):
        data = self.validate(Handler.__schema__)
        times = data.get('times', 1)
        episode = None
        with new_session() as session:
            episodes = session.query(models.Episode.number).filter(
                models.Episode.series_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).order_by(asc(models.Episode.number)).all()
            if not episodes:
                return
            for episode in episodes:
                set_watched(
                    session=session,
                    user_id=self.current_user.id,
                    show_id=show_id,
                    episode_number=episode.number,
                    times=times,
                )
                session.commit()

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    async def delete(self, show_id, from_, to):
        await self._delete(show_id, int(from_), int(to))
        self.set_status(204)

    @run_on_executor
    def _delete(self, show_id, from_, to):
        with new_session() as session:
            ews = session.query(models.Episode_watched).filter(
                models.Episode_watched.series_id == show_id,
                models.Episode_watched.user_id == self.current_user.id,
                models.Episode_watched.episode_number >= from_,
                models.Episode_watched.episode_number <= to,
            ).order_by(asc(models.Episode_watched.episode_number)).all()
            for ew in ews:
                ew.set_prev_as_watching()
                session.delete(ew)
            session.commit()