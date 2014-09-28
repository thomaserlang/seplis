import logging
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, Numeric, \
    ForeignKey, event, TIMESTAMP, Date, SmallInteger, CHAR, TypeDecorator, VARCHAR
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types
from sqlalchemy.dialects import postgresql
from sqlalchemy import asc, desc, and_
from sqlalchemy.orm import relationship, remote, deferred
from seplis.utils import json_dumps, json_loads
from seplis.api import exceptions

base = declarative_base()

def row_to_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

def sort_parser(sort, sort_lookup, sort_list=None):
    '''
    Parses a list of string sort types to SQLAlchemy field sorts.

    Example:

        sort_lookup = {
            'journal_entry_id': models.Journal_entry.id,
            'patient': {
                'first_name': models.Patient.first_name,
            }
        }

        sort = sort_parser(
            'patient.first_name, -journal_entry_id',
            sort_lookup
        )

        session.query(
            models.Patient,
            models.Journal_entry,
        ).order_by(
            *sort
        )

    :param sort: [`str`]
    :param sort_lookup: [`SQLAlchemy model field`]
    :returns: [`SQLAlchemy model sort field`]
    '''
    if sort_list == None:
        sort_list = []
    sort = filter(None, sort.split(','))
    for s in sort:
        if '.' in s:
            sub = s.split('.', 1)
            key = sub[0]
            if not isinstance(sort_lookup[key], dict):
                continue
            if len(sub) == 2:
                sort_parser(sub[1], sort_lookup[key], sort_list)
            continue
        sort_type = asc
        s = s.strip()
        if s.endswith(':desc'):
            sort_type = desc
            s = s[:-5]
        elif s.endswith(':asc'):
            s = s[:-4]
        if s not in sort_lookup or isinstance(sort_lookup[s], dict):
            raise exceptions.Sort_not_allowed(s)
        sort_list.append(
            sort_type(
                sort_lookup[s]
            )
        )
    return sort_list

class JSONEncodedDict(TypeDecorator):  
    impl = Text  
  
    def process_bind_param(self, value, dialect):
        if value is None:  
            return None
        if isinstance(value, str):
            return value
        return json_dumps(value)
  
    def process_result_value(self, value, dialect):  
        if not value:  
            return None
        return json_loads(value)  

class Show(base):
    __tablename__ = 'shows'

    id = Column(Integer, autoincrement=True, primary_key=True)

    created = Column(DateTime)
    updated = Column(DateTime)
    status = Column(Integer, server_default='0', nullable=False)
    fans = Column(Integer, server_default='0')

    title = Column(String(200), unique=True)
    description_text = Column(Text)
    description_title = Column(String(45))
    description_url = Column(String(200))
    premiered = Column(Date)
    ended = Column(Date)
    externals = Column(JSONEncodedDict())
    index_info = Column(String(45))
    index_episodes = Column(String(45))
    index_images = Column(String(45))
    seasons = Column(JSONEncodedDict())
    runtime = Column(Integer)
    genres = Column(JSONEncodedDict())
    alternate_titles = Column(JSONEncodedDict())
    image_id = Column(Integer, ForeignKey('images.id'))
    image = relationship('Image')

class Episode(base):
    __tablename__ = 'episodes'

    show_id = Column(Integer, primary_key=True)
    number = Column(Integer, primary_key=True)
    title = Column(String(200), unique=True)
    air_date = Column(Date)    
    description_text = Column(Text)
    description_title = Column(String(45))
    description_url = Column(String(200))
    season = Column(Integer)
    episode = Column(Integer)
    runtime = Column(Integer)

class Show_external(base):
    __tablename__ = 'show_externals'

    show_id = Column(Integer, primary_key=True)
    title = Column(String(45), primary_key=True)
    value = Column(String(45))

class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), unique=True)
    email = Column(String(100), unique=True)
    password = Column(CHAR(87))
    created = Column(DateTime)
    level = Column(Integer)

    fan_of = Column(Integer, server_default='0')
    watched = Column(Integer, server_default='0')

class App(base):
    __tablename__ = 'apps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    name = Column(String(45))
    client_id = Column(String(45))
    client_secret = Column(String(45))
    redirect_uri = Column(String(45))
    level = Column(Integer)
    created = Column(DateTime)
    updated = Column(DateTime)

class Token(base):
    __tablename__ = 'tokens'

    user_id = Column(Integer)
    app_id = Column(Integer)
    token = Column(String(45), primary_key=True)
    expires = Column(DateTime)
    user_level = Column(Integer)

class Show_fan(base):
    __tablename__ = 'show_fans'

    show_id = Column(Integer, primary_key=True, autoincrement=False)
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    datetime = Column(DateTime)

class Episode_watched(base):
    __tablename__ = 'episodes_watched'

    show_id = Column(Integer, primary_key=True, autoincrement=False)
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    episode_number = Column(Integer, primary_key=True, autoincrement=False)
    times = Column(Integer, default=0)
    position = Column(Integer)
    datetime = Column(DateTime)

class Show_watched(base):
    __tablename__ = 'shows_watched'

    show_id = Column(Integer, primary_key=True, autoincrement=False)
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    episode_number = Column(Integer, autoincrement=False)
    position = Column(Integer)
    datetime = Column(DateTime)

class Tag(base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(String(100))
    type = Column(String(50))

class Tag_relation(base):
    __tablename__ = 'tag_relations'

    user_id = Column(Integer, primary_key=True, autoincrement=False)
    type = Column(String(50), primary_key=True, autoincrement=False)
    relation_id = Column(Integer, primary_key=True, autoincrement=False)
    tag_id = Column(Integer, primary_key=True, autoincrement=False)

class Image(base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    relation_type = Column(Integer)
    relation_id = Column(Integer)
    external_name = Column(String(50))
    external_id = Column(String(50))
    height = Column(Integer)
    width = Column(Integer)
    hash = Column(String(64))
    source_title = Column(String(200))
    source_url = Column(String(200))
    created = Column(DateTime)
    type = Column(Integer)