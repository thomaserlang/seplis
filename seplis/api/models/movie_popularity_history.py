import sqlalchemy as sa
from .base import Base


class Movie_popularity_history(Base):
    __tablename__ = 'movie_popularity_history'

    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    date = sa.Column(sa.Date, primary_key=True)
    popularity = sa.Column(sa.DECIMAL(precision=12, scale=4), nullable=False)