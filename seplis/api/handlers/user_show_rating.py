import good
from datetime import datetime
from seplis.api.handlers import base
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api import models, exceptions, constants
from seplis import schemas


class Handler(base.Handler):

    __schema__ = good.Schema({
        'rating': good.All(int, good.Range(min=1, max=10)),
    })

    @authenticated(0)
    async def put(self, show_id):
        await self.save(show_id)
        self.set_status(204)

    @authenticated(0)
    async def get(self, show_id):
        r = await self.get_rating(show_id)
        self.write_object(r)

    @authenticated(0)
    async def delete(self, show_id):
        await self.delete_rating(show_id)
        self.set_status(204)

    @run_on_executor
    def save(self, show_id):
        d = self.validate()
        with new_session() as session:
            r = models.Series_user_rating(
                show_id=show_id,
                user_id=self.current_user.id,
                rating=d['rating'],
                updated_at=datetime.utcnow(),
            )
            session.merge(r)
            session.commit()

    @run_on_executor
    def get_rating(self, show_id):
        with new_session() as session:
            r = session.query(models.Series_user_rating.rating).filter(
                models.Series_user_rating.user_id == self.current_user.id,
                models.Series_user_rating.show_id == show_id,
            ).first()
            return {
                'rating': r.rating if r else None,
            }

    @run_on_executor
    def delete_rating(self, show_id):
        with new_session() as session:
            session.query(models.Series_user_rating).filter(
                models.Series_user_rating.user_id == self.current_user.id,
                models.Series_user_rating.show_id == show_id,
            ).delete()
            session.commit()
