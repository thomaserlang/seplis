import logging
from sqlalchemy import select, update, orm
from tornado import web
from seplis import tasks
from seplis.api.decorators import authenticated
from seplis.api.handlers import base
from seplis.api import constants, exceptions, models, schemas
from seplis.api.connections import database
from seplis import utils

class Handler(base.Handler):

    __schema__ = schemas.Movie_create

    async def get(self, movie_id: str):
        async with self.async_session() as session:
            q = select(models.Movie).where(models.Movie.id == movie_id)
            r = await session.scalars(q)
            movie = r.first()
            if not movie:
                raise exceptions.Not_found()
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def post(self):
        m: schemas.Movie_create = self.validate()
        async with self.async_session() as session:
            movie = await models.Movie.save(session, movie_id=None, movie_data=m, patch=False)
            await session.commit()
            database.queue.enqueue(
                tasks.update_movie,
                int(movie.id),
                result_ttl=0,
            )
            self.set_status(201)
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def put(self, movie_id: str):
        m: schemas.Movie_create = self.validate()
        async with self.async_session() as session:
            movie = await models.Movie.save(session, movie_id=movie_id, movie_data=m, patch=False)
            await session.commit()
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def patch(self, movie_id: str):
        m: schemas.Movie_create = self.validate()
        async with self.async_session() as session:
            movie = await models.Movie.save(session, movie_id=movie_id, movie_data=m, patch=True)
            await session.commit()
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def delete(self, movie_id: str):
        async with self.async_session() as session:
            await session.execute(update(models.Movie).values(status=-1).where(
                models.Movie.id == movie_id,
            ))
            await session.commit()
            self.set_status(204)


class Update_handler(base.Handler):

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def post(self, movie_id):
        job = database.queue.enqueue(
            tasks.update_movie,
            int(movie_id),
            result_ttl=0,
        )
        self.write_object({
            'job_id': job.id,
        })



class Play_servers_handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    async def get(self, movie_id):
        async with self.async_session() as session:
            results = await session.scalars(select(models.Play_server).where(
                models.Play_server_access.user_id == self.current_user.id,
                models.Play_server.id == models.Play_server_access.play_server_id,
            ).options(
                orm.undefer_group('secret')
            ))
            playids = []
            for r in results:
                playids.append({
                    'play_id': web.create_signed_value(
                        secret=r.secret,
                        name='play_id',
                        value=utils.json_dumps({
                            'type': 'movie',
                            'movie_id': int(movie_id),
                        }),
                        version=2,
                    ).decode('utf-8'),
                    'play_url': r.url,
                })
        self.write_object(playids)