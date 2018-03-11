import uuid
import sqlalchemy as sa
from .base import Base
from seplis import utils
from datetime import datetime

class Play_server(Base):
    __tablename__ = 'play_servers'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    external_id = sa.Column(sa.String(36))
    url = sa.orm.deferred(sa.Column(sa.String(200)), group='secret')
    secret = sa.orm.deferred(sa.Column(sa.String(200)), group='secret')

    def __init__(self, user_id, name, url, secret):
        self.user_id = user_id
        self.name = name
        self.url = url
        self.secret = secret
        self.external_id = str(uuid.uuid4())

    def serialize(self):
        return utils.row_to_dict(self)

    def after_insert(self):
        ps = Play_access(
            play_server_id=self.id,
            user_id=self.user_id,
        )
        self.session.add(ps)

class Play_access(Base):
    __tablename__ = 'play_access'

    play_server_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, primary_key=True)

