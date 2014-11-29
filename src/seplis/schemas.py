import re
import aniso8601
from voluptuous import Schema, Any, Required, Length, All, Match, \
    Invalid, Range, Optional
from datetime import datetime
from dateutil import parser
from seplis.api import constants

def validate(schema, d, *arg, **args):
    if not isinstance(schema, Schema):            
        schema = Schema(schema, *arg, **args)    
    return schema(d)   

def iso8601():
    def f(v):    
        try:
            return parser.parse(v)
        except:
            raise Invalid('invalid iso 8601 datetime {}'.format(v))
    return f

def date_():
    def f(v):    
        try:
            return aniso8601.parse_date(v)
        except:
            raise Invalid('invalid date {}'.format(v))
    return f

def time_(msg=None):
    def f(v):    
        try:
            return aniso8601.parse_time(v)
        except:
            raise Invalid('invalid time {}'.format(v))
    return f

def image_type(msg=None):
    def f(v):
        if v not in constants.IMAGE_TYPES:
            raise Invalid('invalid image type: {}'.format(v))
        return v
    return f

def validate_email(email):
    """Validate email."""
    if not "@" in email:
        raise Invalid("this is an invalid email address")
    return email

def SHOW_EPISODE_TYPE(msg=None):
    def f(v):
        if v not in constants.SHOW_EPISODE_TYPE:
            raise Invalid('invalid episodes type: {}'.format(v))
        return v
    return f

Description_schema = Schema({
    'text': Any(None, str),
    'title': Any(None, str),
    'url':  Any(None, str),
})
Episode_schema = {
    'title': Any(str, None),
    Required('number'): int,
    Optional('season'): Any(int, None),
    Optional('episode'): Any(int, None),
    'air_date': Any(None, datetime, date_()),
    'description': Any(None, Description_schema),
    'runtime': Any(int, None),
}
External_schema = Schema({
    All(Length(min=1, max=45)):Any(None, All(str, Length(min=1, max=45)))
})
Index_schema = Schema(
    {key: Any(None, All(str, Length(min=1, max=45))) \
        for key in constants.INDEX_TYPE_NAMES}
)
Show_schema = {
    'title': str,
    'description': Any(None, Description_schema),
    'premiered': Any(None, datetime, date_()),
    'ended': Any(None, datetime, date_()),
    Optional('episodes'): Any([Episode_schema]),
    'externals': Any(None, External_schema),
    'indices': Any(None, Index_schema),
    'status': int,
    'runtime': Any(int, None),
    'genres': [str],
    'alternative_titles': [str],
    'poster_image_id': Any(int, None),
    'episode_type': All(int, SHOW_EPISODE_TYPE()),   
}

User_schema = Schema({
    'name': All(
        str, 
        Length(min=1, max=45), 
        Match(re.compile(r'^[a-z0-9-_]+$', re.I),
        msg='must only contain a-z, 0-9, _ and -')
    ),    
    'email': All(str, Length(min=1, max=100), validate_email),
    'password': All(str, Length(min=6)),
}, required=True)

App_schema = Schema({
    'name': All(str, Length(min=1, max=45)),
    'redirect_uri': All(str, Length(1, max=45)),
    'level': int,
})

Token = Schema({
    'grant_type': str,
}, extra=True, required=True)

Token_type_password = Schema({
    'grant_type': str,
    'email': str,
    'password': str,
    'client_id': str,
}, extra=False, required=True)

User_tag_relation_schema = Schema({
    'name': All(str, Length(min=1, max=50)),
}, required=True)

Episode_watched = Schema({
    Optional('times'): int,
    Optional('position'): int,
})

Image = {
    'external_name': All(str, Length(min=1, max=45)),
    'external_id': All(str, Length(min=1, max=45)),
    'source_title': All(str, Length(min=1, max=200)),
    'source_url': All(str, Length(min=1, max=200)),
    'type': All(int, image_type()),
}

Play_server = {
    'name': All(str, Length(min=1, max=45)),
    'url': All(str, Length(min=1, max=200)),
    'secret': All(str, Length(min=1, max=200)),
}

Config_play_scan = Schema(
    Any(
        None, 
        [
            Schema({
                'type': str,
                'path': str,
            }, required=True)
        ]
    )
)