import asyncio
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.mysql import insert
from seplis.api import models, constants, schemas
from seplis.api.decorators import authenticated
from seplis.api.handlers import base

class Watched_schema(BaseModel):
    watched_at: Optional[datetime] = schemas.default_datetime

    class Config:
        extra = 'forbid'

class Handler(base.Handler):

    __schema__ = Watched_schema

    @authenticated(constants.LEVEL_PROGRESS)
    async def get(self, movie_id):
        async with self.async_session() as session:
            r = await self.get_watched(session, movie_id)
            if r:
                self.write_object(r)
            else:
                self.set_status(204)

    @authenticated(constants.LEVEL_PROGRESS)
    async def post(self, movie_id: str):
        data: Watched_schema = self.validate()
        async with self.async_session() as session:
            async with session.begin():
                sql = insert(models.Movie_watched).values(
                    movie_id=movie_id,
                    user_id=self.current_user.id,
                    watched_at=data.watched_at,
                    times=1
                )
                sql = sql.on_duplicate_key_update(
                    watched_at=sql.inserted.watched_at,
                    times=models.Movie_watched.times + 1,
                    position=0,
                )
                sql_history = insert(models.Movie_watched_history).values(
                    movie_id=movie_id,
                    user_id=self.current_user.id,
                    watched_at=data.watched_at,
                )
                await asyncio.gather(
                    session.execute(sql),
                    session.execute(sql_history),
                )
                r = await self.get_watched(session, movie_id)
                await session.commit()                
                self.write_object(r)

    @authenticated(constants.LEVEL_PROGRESS)
    async def delete(self, movie_id: str):
        async with self.async_session() as session:
            async with session.begin():
                w = await self.get_watched(session, movie_id)
                if w.times <= 1:
                    await asyncio.gather(
                        session.execute(delete(models.Movie_watched).where(
                            models.Movie_watched.movie_id == movie_id,
                            models.Movie_watched.user_id == self.current_user.id,
                        )),
                        session.execute(delete(models.Movie_watched_history).where(
                            models.Movie_watched_history.movie_id == movie_id,
                            models.Movie_watched_history.user_id == self.current_user.id,
                        )),
                    )
                    await session.commit()
                    self.set_status(204)
                else:
                    watched_at = await session.scalar(select(models.Movie_watched_history.watched_at).where(
                        models.Movie_watched_history.movie_id == movie_id,
                        models.Movie_watched_history.user_id == self.current_user.id,
                    ).limit(1))
                    if w.position > 0:
                        await session.execute(update(models.Movie_watched).where(
                            models.Movie_watched.movie_id == movie_id,
                            models.Movie_watched.user_id == self.current_user.id,
                        ).values(
                            position=0,
                            watched_at=watched_at,
                        ))
                    else:
                        id_ = await session.scalar(select(models.Movie_watched_history.id).where(
                            models.Movie_watched_history.movie_id == movie_id,
                            models.Movie_watched_history.user_id == self.current_user.id,
                        ).order_by(
                            models.Movie_watched_history.watched_at.desc()
                        ).limit(1))
                        await asyncio.gather(
                            session.execute(update(models.Movie_watched).where(
                                models.Movie_watched.movie_id == movie_id,
                                models.Movie_watched.user_id == self.current_user.id,
                            ).values(
                                times=models.Movie_watched.times - 1,
                                position=0,
                                watched_at=watched_at,
                            )),
                            session.execute(delete(models.Movie_watched_history).where(
                                models.Movie_watched_history.id == id_,
                            ))
                        )
                    r = await self.get_watched(session, movie_id)
                    await session.commit()
                    self.write_object(r)

    async def get_watched(self, session, movie_id: str):
        r = await session.execute(select(
                models.Movie_watched.position,
                models.Movie_watched.times,
                models.Movie_watched.watched_at,
            ).where(
                models.Movie_watched.movie_id == movie_id,
                models.Movie_watched.user_id == self.current_user.id,
            )
        )
        return r.one_or_none()