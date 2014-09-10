from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, Numeric, \
    ForeignKey, event, TIMESTAMP, Date, SmallInteger, CHAR, TypeDecorator, VARCHAR
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types
from sqlalchemy.dialects import postgresql
from seplis.utils import json_dumps, json_loads
base = declarative_base()
import logging

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

    title = Column(String(200), unique=True)
    description_text = Column(Text)
    description_title = Column(String(45))
    description_url = Column(String(200))
    premiered = Column(Date)
    ended = Column(Date)
    externals = Column(JSONEncodedDict())
    index_info = Column(String(45))
    index_episodes = Column(String(45))
    seasons = Column(JSONEncodedDict())
    runtime = Column(Integer)
    genres = Column(JSONEncodedDict())
    alternate_titles = Column(JSONEncodedDict())

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

class Show_follow(base):
    __tablename__ = 'show_followers'

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
    episode_number = Column(Integer, primary_key=True, autoincrement=False)
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