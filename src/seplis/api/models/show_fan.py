import sqlalchemy as sa
from datetime import datetime
from .base import Base

class Show_fan(Base):
    __tablename__ = 'show_fans'

    show_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('shows.id'), 
        primary_key=True, 
        autoincrement=False,
    )
    user_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('users.id'),
        primary_key=True, 
        autoincrement=False,
    )
    created_at = sa.Column(
        sa.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
    )

    def incr_fan(self, amount):
        """Increments the fans counter for the show in es.
        Automatically called on insert and delete.

        :param amount: int
        """
        self.session.es_bulk.append({
            '_op_type': 'update',
            '_index': 'shows',
            '_id': self.show_id,
            'script': 'ctx._source.fans += {}'.format(amount),
        })
        from seplis.api.models import Show
        self.session.execute(Show.__table__.update()\
            .where(Show.__table__.c.id==self.show_id)\
            .values(fans=Show.__table__.c.fans + amount)
        )
        from seplis.api.models import User
        self.session.execute(User.__table__.update()\
            .where(User.__table__.c.id == self.user_id)\
            .values(fan_of=User.__table__.c.fan_of + amount)
        )

    def after_upsert(self):
        self.incr_fan(1)

    def after_delete(self):
        self.incr_fan(-1)