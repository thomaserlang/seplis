import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from seplis.api.decorators import new_session, run_on_executor, authenticated
from seplis.api import models, constants

class Handler(base.Pagination_handler):

    async def get(self, user_id):
        super().get()
        d = await self.fan_of(user_id)
        self.write_object(d)

    @authenticated(constants.LEVEL_USER)
    async def put(self, user_id, show_id):
        await self.fan(user_id, show_id)
        self.set_status(204)

    @authenticated(constants.LEVEL_USER)
    async def delete(self, user_id, show_id):
        await self.unfan(user_id, show_id)
        self.set_status(204)

    @run_on_executor
    def fan_of(self, user_id):
        with new_session() as session:
            pagination = session.query(models.Show).filter(
                models.Show_fan.user_id == user_id,
                models.Show_fan.show_id == models.Show.id,
            ).order_by(
                sa.desc(models.Show_fan.created_at), 
                sa.desc(models.Show_fan.show_id),
            ).paginate(page=self.page, per_page=self.per_page)
            return pagination

    @run_on_executor
    def fan(self, user_id, show_id):
        with new_session() as session:            
            if session.query(models.Show_fan).get((show_id, user_id)):
                return
            fan = models.Show_fan(
                user_id=user_id,
                show_id=show_id,
            )
            session.add(fan)
            session.commit()

    @run_on_executor
    def unfan(self, user_id, show_id):
        with new_session() as session:
            fan = session.query(models.Show_fan).filter(
                models.Show_fan.user_id == user_id,
                models.Show_fan.show_id == show_id,
            ).first()
            if fan:
                session.delete(fan)
                session.commit()