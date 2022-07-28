import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from seplis import utils

base = declarative_base()

class Episode(base):
    __tablename__ = 'episodes'

    show_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.Text)
    meta_data = sa.Column(sa.JSON)
    modified_time = sa.Column(sa.DateTime)

class Episode_number_lookup(base):
    __tablename__ = 'episode_number_lookup'    

    show_id = sa.Column(sa.Integer, primary_key=True)
    lookup_type = sa.Column(sa.Integer, primary_key=True)
    lookup_value = sa.Column(sa.String(45), primary_key=True)
    number = sa.Column(sa.Integer)

class Show_id_lookup(base):
    __tablename__ = 'show_id_lookup'

    file_show_title = sa.Column(sa.String(200), primary_key=True)
    show_title = sa.Column(sa.String(200))
    show_id = sa.Column(sa.Integer)
    updated = sa.Column(sa.DateTime)

class Movie_id_lookup(base):
    __tablename__ = 'movie_id_lookup'

    file_movie_title = sa.Column(sa.String(200), primary_key=True)
    movie_title = sa.Column(sa.String(200))
    movie_id = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.DateTime)

class Movie(base):
    __tablename__ = 'movies'

    movie_id = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.String(400), primary_key=True)
    meta_data = sa.Column(sa.JSON)
    modified_time = sa.Column(sa.DateTime)