import sqlalchemy as sa

from seplis.utils.sqlalchemy import UtcDateTime
base = sa.orm.declarative_base()

class Episode(base):
    __tablename__ = 'episodes'

    series_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer)
    path = sa.Column(sa.Text, primary_key=True)
    meta_data = sa.Column('metadata', sa.JSON)
    modified_time = sa.Column(UtcDateTime)

class Episode_number_lookup(base):
    __tablename__ = 'episode_number_lookup'    

    series_id = sa.Column(sa.Integer, primary_key=True)
    lookup_type = sa.Column(sa.Integer, primary_key=True)
    lookup_value = sa.Column(sa.String(45), primary_key=True)
    number = sa.Column(sa.Integer)

class Series_id_lookup(base):
    __tablename__ = 'series_id_lookup'

    file_title = sa.Column(sa.String(200), primary_key=True)
    series_title = sa.Column(sa.String(200))
    series_id = sa.Column(sa.Integer)
    updated_at = sa.Column(UtcDateTime)

class Movie_id_lookup(base):
    __tablename__ = 'movie_id_lookup'

    file_title = sa.Column(sa.String(200), primary_key=True)
    movie_title = sa.Column(sa.String(200))
    movie_id = sa.Column(sa.Integer)
    updated_at = sa.Column(UtcDateTime)

class Movie(base):
    __tablename__ = 'movies'

    movie_id = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.String(400), primary_key=True)
    meta_data = sa.Column('metadata', sa.JSON)
    modified_time = sa.Column(UtcDateTime)