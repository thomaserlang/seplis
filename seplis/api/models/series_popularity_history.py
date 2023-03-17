import sqlalchemy as sa
from .base import Base


class Series_popularity_history(Base):
    __tablename__ = 'series_popularity_history'

    series_id = sa.Column(sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    date = sa.Column(sa.Date, primary_key=True)
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4), nullable=False)