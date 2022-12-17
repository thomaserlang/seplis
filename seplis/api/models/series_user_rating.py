import sqlalchemy as sa
from .base import Base
from datetime import datetime

class Series_user_rating(Base):
    __tablename__ = 'user_series_ratings'

    user_id = sa.Column(sa.Integer, autoincrement=False, primary_key=True)
    series_id = sa.Column(sa.Integer, autoincrement=False, primary_key=True)
    rating = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)