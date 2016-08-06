from seplis.api.handlers import base
from seplis.api.base.pagination import Pagination
from seplis.api.connections import database
from seplis.api.decorators import new_session, run_on_executor, authenticated
from seplis.api import models, constants

class Handler(base.Pagination_handler):

    async def get(self, user_id):
        super().get()
        pipe = database.redis.pipeline()
        name = models.Show_fan.ck_user_shows(user_id)
        pipe.zcard(name)
        start = (self.page - 1) * self.per_page
        pipe.zrevrange(
            name=name,
            start=start,
            end=(start+self.per_page) - 1,
        )
        total_records, show_ids = pipe.execute()
        shows = []
        if show_ids:
            show_lookup = await self.es('/shows/show/_mget', body={
                'ids': show_ids,
            })
            shows = [d['_source'] for d in show_lookup['docs']]
        self.write_object(Pagination(
            page=self.page,
            per_page=self.per_page,
            records=shows,
            total=total_records,
        ))

    @authenticated(constants.LEVEL_USER)
    async def put(self, user_id, show_id):
        await self.fan(user_id, show_id)
        self.set_status(204)

    @authenticated(constants.LEVEL_USER)
    async def delete(self, user_id, show_id):
        await self.unfan(user_id, show_id)
        self.set_status(204)

    @run_on_executor
    def fan(self, user_id, show_id):
        self.check_user_edit(user_id)
        if self.redis.zrank(models.Show_fan.ck_user_shows(user_id), show_id) != None:
            return
        with new_session() as session:
            fan = models.Show_fan(
                user_id=user_id,
                show_id=show_id,
            )
            session.add(fan)
            session.commit()

    @run_on_executor
    def unfan(self, user_id, show_id):
        self.check_user_edit(user_id)
        if self.redis.zrank(models.Show_fan.ck_user_shows(user_id), show_id) == None:
            return
        with new_session() as session:
            fan = session.query(models.Show_fan).filter(
                models.Show_fan.user_id == user_id,
                models.Show_fan.show_id == show_id,
            ).first()
            if fan:
                session.delete(fan)
                session.commit()