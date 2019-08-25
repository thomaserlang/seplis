import good
import sqlalchemy as sa
from seplis.api.handlers import base
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from seplis.api.decorators import new_session, run_on_executor, authenticated
from seplis.api import models, constants

class Handler(base.Pagination_handler):

    __arguments_schema__ = good.Schema({
        'genre': [str],
    }, default_keys=good.Optional,)

    async def get(self, user_id, show_id=None):
        super().get()
        user_id = self.user_id_or_current(user_id)
        if not show_id:
            d = await self.fan_of(user_id)
        else:
            d = {'is_fan': self.is_fan(user_id, show_id)}
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
        args = self.validate_arguments()
        with new_session() as session:
            query = session.query(models.Show).filter(
                models.Show_fan.user_id == user_id,
                models.Show_fan.show_id == models.Show.id,
            ).order_by(
                sa.desc(models.Show_fan.created_at), 
                sa.desc(models.Show_fan.show_id),
            )
            genres = args.get('genre')
            if genres:
                query = query.filter(
                    models.Show_genre.show_id == models.Show_fan.show_id,
                    models.Show_genre.genre.in_(genres),
                )
            return query.paginate(page=self.page, per_page=self.per_page)

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

    def is_fan(self, user_id, show_id):
        with new_session() as session:
            q = session.query(models.Show_fan.show_id).filter(
                models.Show_fan.user_id == user_id,
                models.Show_fan.show_id == show_id,
            ).first()
            return True if q else False