import orjson, decimal
from collections import OrderedDict
from tornado import escape
from datetime import datetime

def default(obj):
    if isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, 'serialize'):
        return obj.serialize()
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, OrderedDict):
        return dict(obj)
    elif isinstance(obj, datetime):
        return datetime.isoformat()+'Z'
    raise TypeError

def json_dumps(obj):
    return orjson.dumps(
        obj,
        default=default,
        option=orjson.OPT_UTC_Z | orjson.OPT_NAIVE_UTC,
    ).decode('utf-8')

def json_loads(s):
    return orjson.loads(escape.native_str(s))