import orjson, decimal
from collections import OrderedDict
from tornado import escape

def default(obj):
    if isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, 'to_json'):
        return obj.to_json()
    elif hasattr(obj, 'serialize'):
        return obj.serialize()
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, OrderedDict):
        return dict(obj)

def json_dumps(obj):
    return orjson.dumps(
        obj,
        default=default,
    ).decode('utf-8')

def json_loads(s):
    return orjson.loads(escape.native_str(s))