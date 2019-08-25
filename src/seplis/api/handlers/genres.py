import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants

class Handler(base.Handler):

    async def get(self):
        data = await self.get_genres()
        self.write_object(data)

    @run_on_executor
    def get_genres(self):
        with new_session() as session:
            r = session.query(models.Genre).order_by(models.Genre.genre).all()
            return [g.genre for g in r]