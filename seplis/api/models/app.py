import sqlalchemy as sa
from seplis.utils.sqlalchemy import UtcDateTime
from .base import Base
from seplis import utils
from datetime import datetime

class App(Base):
    __tablename__ = 'apps'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(45))
    client_id = sa.Column(sa.String(45))
    client_secret = sa.Column(sa.String(45))
    redirect_uri = sa.Column(sa.String(45))
    level = sa.Column(sa.Integer)
    created = sa.Column(UtcDateTime, default=datetime.utcnow)
    updated = sa.Column(UtcDateTime, onupdate=datetime.utcnow)


    def __init__(self, user_id, name, level, redirect_uri=None):
        '''
        :param user_id: int
        :param name: str
        :param level: int
        :param redirect_uri: str
        '''
        self.user_id = user_id
        self.name = name
        self.level = level
        self.redirect_uri = redirect_uri
        self.client_id = utils.random_key()
        self.client_secret = utils.random_key()
        self.created = datetime.utcnow()