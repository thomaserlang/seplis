from datetime import datetime
from sqlalchemy import delete, insert, select
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated
from seplis.api.handlers import base

class Handler(base.Handler):

    @authenticated(constants.LEVEL_USER)
    async def get(self, movie_id: str):
        async with self.async_session() as session:
            r = await session.scalar(select(models.Movie_stared.created_at).where(
                models.Movie_stared.movie_id == movie_id,
                models.Movie_stared.user_id == self.current_user.id,
            ))
            if r:
                self.write_object({
                    'created_at': r,
                })
            else:
                raise exceptions.Not_found('User hasn\'t stared this show')
    
    @authenticated(constants.LEVEL_USER)
    async def put(self, movie_id: str):
        async with self.async_session() as session:
            await session.execute(insert(models.Movie_stared).values(
                movie_id=movie_id,
                user_id=self.current_user.id,
                created_at=datetime.utcnow(),
            ).prefix_with('IGNORE'))
            self.set_status(204)

    @authenticated(constants.LEVEL_USER)
    async def delete(self, movie_id: str):
        async with self.async_session() as session:
            await session.execute(delete(models.Movie_stared).where(
                models.Movie_stared.movie_id == movie_id,
                models.Movie_stared.user_id == self.current_user.id,
            ))
            self.set_status(204)