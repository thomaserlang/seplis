from datetime import datetime
from pydantic import BaseModel, conint
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from seplis.api import models, constants, schemas
from seplis.api.decorators import authenticated
from seplis.api.handlers import base

class Position_schema(BaseModel):
    position: conint(ge=0)

    class Config:
        extra = 'forbid'

class Handler(base.Handler):

    __schema__ = Position_schema

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, movie_id):
        async with self.async_session() as session:
            r = await self.get_position(session, movie_id)
            if r:
                self.write_object(r)
            else:
                self.set_status(204)

    @authenticated(constants.LEVEL_PROGRESS)
    async def put(self, movie_id: str):
        data: Position_schema = self.validate()
        async with self.async_session() as session:
            async with session.begin():
                sql = insert(models.Movie_watched).values(
                    movie_id=movie_id,
                    user_id=self.current_user.id,
                    watched_at=datetime.utcnow(),
                    position=data.position,
                )
                sql = sql.on_duplicate_key_update(
                    watched_at=sql.inserted.watched_at,
                    position=sql.inserted.position,
                )
                await session.execute(sql)
                r = await self.get_position(session, movie_id)
                await session.commit()                
                self.write_object(r)

    async def get_position(self, session, movie_id: str):
        r = await session.execute(select(
            models.Movie_watched.position,
            models.Movie_watched.times,
            models.Movie_watched.watched_at,
        ).where(
            models.Movie_watched.movie_id == movie_id,
            models.Movie_watched.user_id == self.current_user.id,
        ))
        return r.one_or_none()