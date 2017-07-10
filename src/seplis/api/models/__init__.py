import logging
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, Numeric, \
    ForeignKey, event, TIMESTAMP, Date, SmallInteger, CHAR, TypeDecorator, VARCHAR
from sqlalchemy import types
from sqlalchemy import asc, desc, and_
from sqlalchemy.orm import relationship, remote, deferred
from seplis.utils import json_dumps, json_loads
from seplis.api import exceptions
from seplis.utils import JSONEncodedDict

from .base import Base
from .show import Show, Show_fan, Show_external
from .image import Image
from .episode import Episode, Episode_watched
from .user import User, Token, User_show_subtitle_lang
from .app import App
from .play_server import Play_server

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(String(100))
    type = Column(String(50))

class Tag_relation(Base):
    __tablename__ = 'tag_relations'

    user_id = Column(Integer, primary_key=True, autoincrement=False)
    type = Column(String(50), primary_key=True, autoincrement=False)
    relation_id = Column(Integer, primary_key=True, autoincrement=False)
    tag_id = Column(Integer, primary_key=True, autoincrement=False)