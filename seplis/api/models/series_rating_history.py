import sqlalchemy as sa
from .base import Base


class Series_rating_history(Base):
    __tablename__ = 'series_rating_history'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    date = sa.Column(sa.Date, primary_key=True)
    rating = sa.Column(sa.DECIMAL(4, 2), nullable=False)
    votes = sa.Column(sa.Integer, nullable=False)