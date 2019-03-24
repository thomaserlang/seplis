import uuid
import sqlalchemy as sa
from .base import Base
from datetime import datetime, timedelta

def _uuid():
    return str(uuid.uuid4())

def _expires():
    return datetime.utcnow() + timedelta(hours=1)

class Reset_password(Base):
    __tablename__ = 'reset_password'

    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    key = sa.Column(sa.String, primary_key=True, default=_uuid)
    expires = sa.Column(sa.DateTime, default=_expires)