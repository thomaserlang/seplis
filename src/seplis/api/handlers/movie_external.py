from sqlalchemy import select
from seplis.api import exceptions, models
from seplis.api.handlers import base

class Handler(base.Handler):

    async def get(self, external_title, external_id):
        async with self.async_session() as session:
            movie = await session.scalar(select(models.Movie).where(
                models.Movie_external.title == external_title,
                models.Movie_external.value == external_id,
                models.Movie.id == models.Movie_external.movie_id,
            ))
            if not movie:
                raise exceptions.Not_found()
            self.write_object(movie)