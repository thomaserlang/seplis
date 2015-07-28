from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session
from seplis.api import models, exceptions
from seplis import schemas
from tornado import gen, web
from tornado.concurrent import run_on_executor

class Handler(base.Handler):

    _schema = {
        schemas.Optional('times'): schemas.All(
            int, 
            schemas.Range(min=-20, max=20)
        ),
    }

    @authenticated(0)
    @gen.coroutine
    def put(self, user_id, show_id, episode_number):
        w = yield self._put(user_id, show_id, episode_number)
        self.write_object(models.Episode_watched.get(
            user_id=user_id,
            show_id=show_id,
            episode_number=episode_number,
        ))

    @run_on_executor
    def _put(self, user_id, show_id, episode_number):
        self.validate()
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            episode.watched(
                user_id=user_id,
                times=int(self.request.body.get('times', 1)),
                position=0,
            )
            session.commit()

    @authenticated(0)
    @gen.coroutine
    def delete(self, user_id, show_id, episode_number):
        yield self._delete(user_id, show_id, episode_number)

    @run_on_executor
    def _delete(self, user_id, show_id, episode_number):
        with new_session() as session:
            episode = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number == episode_number,
            ).first()
            if not episode:
                raise exceptions.Episode_unknown()
            episode.unwatch(user_id)
            session.commit()

    @authenticated(0)
    def get(self, user_id, show_id, episode_number):
        w = models.Episode_watched.get(
            user_id=user_id,
            show_id=show_id,
            episode_number=episode_number,
        )
        if not w:
            raise exceptions.Not_found('the user has not watched this episode')
        self.write_object(w)

class Range_handler(base.Handler):

    @authenticated(0)
    @gen.coroutine
    def put(self, user_id, show_id, from_, to):
        yield self._put(
            user_id, 
            show_id, 
            int(from_), 
            int(to),
        )

    @run_on_executor
    def _put(self, user_id, show_id, from_, to):
        self.validate(Handler._schema)
        times = int(self.request.body.get('times', 1))

        with new_session() as session:
            episodes = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).all()
            for episode in episodes:
                episode.watched(user_id, times=times, position=0)     
            session.commit()

    @authenticated(0)
    @gen.coroutine
    def delete(self, user_id, show_id, from_, to):
        yield self._delete(
            user_id, 
            show_id, 
            int(from_), 
            int(to),
        )

    @run_on_executor
    def _delete(self, user_id, show_id, from_, to):
        with new_session() as session:
            episodes = session.query(models.Episode).filter(
                models.Episode.show_id == show_id,
                models.Episode.number >= from_,
                models.Episode.number <= to,
            ).all()
            for episode in episodes:
                episode.unwatch(user_id)
            session.commit()