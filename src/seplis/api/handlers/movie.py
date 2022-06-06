from typing import Dict, List
from sqlalchemy import delete, insert, select, update
from seplis.api.decorators import authenticated
from seplis.api.handlers import base
from seplis.api import constants, exceptions, models, schemas


class Handler(base.Handler):

    __schema__ = schemas.Movie_schema

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
        m: schemas.Movie_schema = self.validate()
        async with self.async_session() as session:
            movie = await models.Movie.save(session, movie_id=None, movie=m, patch=False)
            await session.commit()
            self.set_status(201)
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def put(self, movie_id: str):
        m: schemas.Movie_schema = self.validate()
        async with self.async_session() as session:
            movie = await models.Movie.save(session, movie_id=movie_id, movie=m, patch=False)
            await session.commit()
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def patch(self, movie_id: str):
        m: schemas.Movie_schema = self.validate()
        async with self.async_session() as session:
            movie = await models.Movie.save(session, movie_id=movie_id, movie=m, patch=True)
            await session.commit()
            self.write_object(movie)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def delete(self, movie_id: str):
        async with self.async_session() as session:
            await session.execute(update(models.Movie).values(status=-1).where(
                models.Movie.id == movie_id,
            ))
            self.set_status(204)