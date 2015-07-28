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
from .user import User, Token
from .app import App
from .play_server import Play_server

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