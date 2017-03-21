import logging
import good
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session
from seplis.api import models, exceptions, constants
from tornado import gen, web
from tornado.concurrent import run_on_executor
from sqlalchemy import asc

class Handler(base.Handler):

    __schema__ = good.Schema({
        'times': good.All(
            int, 
            good.Range(min=-20, max=20)
        ),
    }, default_keys=good.Optional)

    @authenticated(constants.LEVEL_PROGRESS)
    @gen.coroutine
    def put(self, show_id, episode_number):
        w = yield self._put(show_id, episode_number)
        self.write_object(models.Episode_watched.cache_get(
            user_id=self.current_user.id,
            show_id=show_id,
            episode_number=episode_number,
        ))

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
                times=int(self.request.body.get('times', 1)),
                position=0,
            )
            session.commit()

    @authenticated(0)
    @gen.coroutine
    def delete(self, show_id, episode_number):
        yield self._delete(show_id, episode_number)

    @run_on_executor
    def _delete(self, show_id, episode_number):
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            episode.unwatch(self.current_user.id)
            session.commit()

    @authenticated(constants.LEVEL_USER)
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

class Range_handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def put(self, show_id, from_, to):
        yield self._put(
            show_id, 
            int(from_), 
            int(to),
        )
        self.set_status(204)

    @run_on_executor
    def _put(self, show_id, from_, to):
        self.validate(Handler.__schema__)
        times = int(self.request.body.get('times', 1))
        episode = None
        with new_session() as session:
            episodes = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).order_by(asc(models.Episode.number)).all()

            # TODO: fix the commit order...
            for episode in episodes:
                if episode == episodes[-1]:
                    continue# skip the last episode
                episode.watched(self.current_user.id, times=times, position=0)
            if episodes:
                session.commit()
                episode.watched(self.current_user.id, times=times, position=0)
                session.commit()

    @authenticated(constants.LEVEL_USER)
    @gen.coroutine
    def delete(self, show_id, from_, to):
        yield self._delete(
            show_id, 
            int(from_), 
            int(to),
        )
        self.set_status(204)

    @run_on_executor
    def _delete(self, show_id, from_, to):
        with new_session() as session:
            episodes = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).order_by(asc(models.Episode.number)).all()
            for episode in episodes:
                episode.unwatch(self.current_user.id)
            session.commit()