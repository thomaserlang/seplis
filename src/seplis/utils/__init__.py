import base64
import time
import os
import datetime
import re
import tornado.escape
import collections
import json
import codecs
import mimetypes
import sys
import uuid
import io
import sqlalchemy as sa

from . import sqlalchemy
from .validate import *

def random_key():
    return base64.b64encode(
        os.urandom(30)
    ).decode('utf-8')

class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if isinstance(value, set):
            return list(value)
        if hasattr(value, 'serialize'):
            return value.serialize()    
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return super(JsonEncoder, self).default(value)

def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO 8601 format.

    Otherwise, return None.
    """
    if isinstance(value, (datetime.datetime, datetime.time)):
        return isoformat(value)
    elif isinstance(value, datetime.date):
        return value.isoformat()

def isoformat(dt):
    r = dt.isoformat()
    if not dt.tzinfo:
        r += 'Z'
    return r
        
def json_dumps(obj, **kwargs):
    '''
    Turns a object into a json string.

    :param obj: object
    :returns: str
    '''
    return json.dumps(
        obj,
        cls=JsonEncoder,
        **kwargs
    ).replace("</", "<\\/")

def json_loads(s, charset='utf-8'):
    if isinstance(s, bytes):
        s = s.decode(charset)
    return json.loads(s)

def slugify(text, delim='-', max_length=45):
    from slugify import slugify
    result = slugify(
        text if text else '', 
        to_lower=True, 
        max_length=max_length,
        separator=delim,
    )
    return result if result else 'no-title'

def dict_update(d1, d2):
    '''
    Updates values in `d1` with `d2`. 
    Sub dicts will not be overwritten, but updated instead.

    :param d: dict
    :param update: dict
    '''
    for key in d2:
        if key in d1:
            if isinstance(d1[key], dict):
                d1[key].update(d2[key])
            else:
                d1[key] = d2[key]
        else:
            d1[key] = d2[key]
    return d1

def not_redis_none(v):
    if v and (v != b'None'):
        return True
    return False

def decode_dict(d, decoding='utf-8'):
    return {k.decode(decoding): v.decode(decoding) for k, v in d.items()}

def url_encode_tornado_arguments(arguments):
    '''
    Converts the following:

        {
            'param1': ['a', 'b'],
            'param2': ['c'],
        }

    into the following string:

        param1=a&param1=b&param2=c

    :arguemnts: dict
    :returns: str
    '''
    return '&'.join(
        ['{}={}'.format(arg, tornado.escape.url_escape(value.decode('utf-8') \
            if isinstance(value, bytes) else str(value))) \
                for arg in arguments for value in arguments[arg]]
    )

def parse_link_header(link_header):
    '''
    Parses a Link header into a dict according to: http://tools.ietf.org/html/rfc5988#page-6.
    
    Example:
        
        <https://api.example.com/1/users?page=2&per_page=1>; rel="next", <https://api.example.com/1/users?page=3&per_page=1>; rel="last"
    
    Turns into:

        {
            'next': 'https://api.example.com/1/users?page=2&per_page=1',
            'last': 'https://api.example.com/1/users?page=3&per_page=1'
        }

    :param link_header: str
    :returns: dict
    '''
    links = link_header.split(',')
    parsed_links = {}
    for link in links:
        segments = link.split(';')
        if len(segments) < 2:
            continue
        link_part = segments.pop(0).strip()
        if not link_part.startswith('<') or not link_part.endswith('>'):
            continue
        link_part = link_part[1:-1]
        for segment in segments:
            rel = segment.strip().split('=')
            if len(rel) < 2 or rel[0] != 'rel':
                continue
            rel_value = rel[1]
            if rel_value.startswith('"') and rel_value.endswith('"'):
                rel_value = rel_value[1:-1]
            parsed_links[rel_value] = link_part
    return parsed_links


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

def keys_to_remove(keys, d):
    '''
    Removes one or more keys from a dict.

    :param keys: list of str
    :param d: dict
    '''
    for key in keys:
        if key in d:
            del d[key]

def keys_to_keep(keys, d):
    '''
    Removes keys from d that are not in `keys`.

    :param keys: list of str
    :param d: dict
    '''
    for key in d:
        if key not in keys:
            del d[key]

# From http://stackoverflow.com/a/18888633
class MultipartFormdataEncoder(object):
    def __init__(self):
        self.boundary = uuid.uuid4().hex
        self.content_type = 'multipart/form-data; boundary={}'.format(self.boundary)

    @classmethod
    def u(cls, s):
        if sys.hexversion < 0x03000000 and isinstance(s, str):
            s = s.decode('utf-8')
        if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
            s = s.decode('utf-8')
        return s

    def iter(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, file-type) elements for data to be uploaded as files
        Yield body's chunk as bytes
        """
        encoder = codecs.getencoder('utf-8')
        for (key, value) in fields:
            key = self.u(key)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"\r\n').format(key))
            yield encoder('\r\n')
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            yield encoder(self.u(value))
            yield encoder('\r\n')
        for (key, filename, fd) in files:
            key = self.u(key)
            filename = self.u(filename)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
            yield encoder('Content-Type: {}\r\n'.format(mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
            yield encoder('\r\n')
            yield (fd, len(fd))
            yield encoder('\r\n')
        yield encoder('--{}--\r\n'.format(self.boundary))

    def encode(self, fields, files):
        body = io.BytesIO()
        for chunk, chunk_len in self.iter(fields, files):
            body.write(chunk)
        return self.content_type, body.getvalue()

def get_files(path, ext, skip=[]):
    files = []
    for dirname, dirnames, filenames in os.walk(path):
        for file_ in filenames:
            info = os.path.splitext(file_)
            if len(info) != 2:
                continue
            if info[1] != ext:
                continue
            if file_ in skip:
                continue
            files.append(
                os.path.join(dirname, file_)
            )
    return files

class JSONEncodedDict(sa.TypeDecorator):  
    impl = sa.Text  
  
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

    @classmethod
    def empty_list(cls):
        return []

    @classmethod
    def empty_dict(cls):
        return {}

class YesNoBoolean(sa.TypeDecorator):
    true_str = 'Y'
    false_str = 'N'
    impl = sa.Enum(true_str, false_str)

    def process_bind_param(self, value, dialect):
        return self.true_str if value else self.false_str
  
    def process_result_value(self, value, dialect):  
        return True if value == self.true_str else False

class dotdict(dict):
    
    def __getattr__(self, attr):
        return self.get(attr)
    
    __setattr__= dict.__setitem__
    
    __delattr__= dict.__delitem__


def row_to_dict(row):
    return {c.name: getattr(row, c.name) \
        for c in row.__table__.columns}

def _None_check_str(v):
    '''Converts 'None' to None.

    :param v: str
    :returns: str or None
    '''
    if v == 'None':
        return
    return v
def _None_check_int(v):
    if v == 'None':
        return
    return int(v)

def redis_sa_model_dict(rd, cls):
    '''Takes a dict returned from redis and
    converts values to the same type as specified 
    in the model.

    :param rd: dict from redis
    :param cls: SQLAlchemy model class
    '''
    types = {
        sa.Integer: _None_check_int,
        sa.DateTime: _None_check_str,
        sa.String: _None_check_str,
    }
    for key in rd:
        if not key in cls.__table__.columns:
            continue
        t = types.get(
            type(cls.__table__.columns[key].type)
        )
        if t:
            rd[key] = t(rd[key])
    return rd