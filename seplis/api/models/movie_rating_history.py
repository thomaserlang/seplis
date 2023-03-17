import sqlalchemy as sa
from .base import Base


class Movie_rating_history(Base):
    __tablename__ = 'movie_rating_history'

    movie_id = sa.Column(sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    date = sa.Column(sa.Date, primary_key=True)
    rating = sa.Column(sa.DECIMAL(4, 2), nullable=False)
    votes = sa.Column(sa.Integer, nullable=False)