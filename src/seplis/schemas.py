import re, good, aniso8601, logging
from dateutil import parser, tz
from seplis.api import constants

def validate(schema, d, *arg, **args):
    if not isinstance(schema, good.Schema):            
        schema = good.Schema(schema, *arg, **args)    
    return schema(d)   

def iso8601():
    def f(v):    
        try:
            return aniso8601.parse_datetime(v)
        except:
            raise good.Invalid('invalid iso 8601 datetime {}'.format(v))
    return f

def iso8601_to_utc():
    def f(v):
        try:
            d = aniso8601.parse_datetime(v)
            d = d.replace(microsecond=0)
            if d.tzinfo:
                d = d.astimezone(tz.tzutc())
            return d
        except:
            raise good.Invalid('invalid iso 8601 datetime {}'.format(v))
    return f

def date_():
    def f(v):    
        try:
            return aniso8601.parse_date(v)
        except:
            raise good.Invalid('invalid date {}'.format(v))
    return f

def time_(msg=None):
    def f(v):    
        try:
            return aniso8601.parse_time(v)
        except:
            raise good.Invalid('invalid time {}'.format(v))
    return f

def image_type(msg=None):
    def f(v):
        if v not in constants.IMAGE_TYPES:
            raise good.Invalid('invalid image type: {}'.format(v))
        return v
    return f

def validate_email(email):
    """Validate email."""
    if not "@" in email:
        raise good.Invalid("this is an invalid email address")
    return email

def SHOW_EPISODE_TYPE(msg=None):
    def f(v):
        if v not in constants.SHOW_EPISODE_TYPE:
            raise good.Invalid('invalid episodes type: {}'.format(v))
        return v
    return f

Description_schema = good.Schema({
    'text': good.Maybe(str),
    'title': good.Maybe(str),
    'url':  good.Maybe(str),
}, default_keys=good.Optional)
_Episode_schema = {
    'title': good.Maybe(str),
    good.Required('number'): good.All(good.Coerce(int), good.Range(min=1)),
    good.Optional('season'): good.Maybe(good.All(good.Coerce(int), good.Range(min=1))),
    good.Optional('episode'): good.Maybe(good.All(good.Coerce(int), good.Range(min=1))),
    'air_date': good.Maybe(date_()),
    'air_time': good.Maybe(time_()),
    'air_datetime': good.Maybe(iso8601_to_utc()),
    'description': good.Any(None, Description_schema),
    'runtime': good.Maybe(good.Coerce(int)),
}
Episode_schema = good.Schema(_Episode_schema, default_keys=good.Optional)
External_schema = good.Schema({
    good.All(good.Length(min=1, max=45)):good.Any(None, good.All(good.Coerce(str), good.Length(min=1, max=45)))
}, default_keys=good.Optional)
Importer_schema = good.Schema(
    {key: good.Maybe(good.All(str, good.Length(min=1, max=45))) \
        for key in constants.IMPORTER_TYPE_NAMES},
    default_keys=good.Optional,
)
_Show_schema = {
    'title': good.Maybe(str),
    'description': good.Maybe(Description_schema),
    'premiered': good.Maybe(date_()),
    'ended': good.Maybe(date_()),
    good.Optional('episodes'): [Episode_schema],
    'externals': good.Any(None, External_schema),
    'importers': good.Any(None, Importer_schema),
    'status': good.Coerce(int),
    'runtime': good.Maybe(good.Coerce(int)),
    'genres': [str],
    'alternative_titles': [str],
    'poster_image_id': good.Maybe(good.Coerce(int)),
    'episode_type': good.All(good.Coerce(int), SHOW_EPISODE_TYPE()),   
    'language': good.Maybe(good.All(str, good.Length(min=1, max=100))),
}
Show_schema = good.Schema(_Show_schema, default_keys=good.Optional)

App_schema = good.Schema({
    'name': good.All(str, good.Length(min=1, max=45)),
    'redirect_uri': good.All(str, good.Length(1, max=45)),
    'level': int,
}, default_keys=good.Optional)

Token = good.Schema({
    'grant_type': str,
}, extra_keys=good.Allow)

Token_type_password = good.Schema({
    'grant_type': str,
    'email': str,
    'password': str,
    'client_id': str,
})

_Image = {
    'external_name': good.All(str, good.Length(min=1, max=45)),
    'external_id': good.All(str, good.Length(min=1, max=45)),
    'source_title': good.All(str, good.Length(min=1, max=200)),
    'source_url': good.All(str, good.Length(min=1, max=200)),
    'type': good.All(int, image_type()),
}
Image_required = good.Schema(_Image, default_keys=good.Required)
Image_optional = good.Schema(_Image, default_keys=good.Optional)

Config_play_scan = good.Schema(
    good.Any(
        None, 
        [
            {
                'type': str,
                'path': str,
            }
        ]
    )
)