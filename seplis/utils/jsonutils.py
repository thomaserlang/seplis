import orjson, decimal
from collections import OrderedDict
from datetime import datetime
from sqlalchemy.engine import Row
from pydantic import BaseModel
from seplis import logger

def default(obj):
    if isinstance(obj, BaseModel):
        return obj.dict()
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, 'serialize'):
        return obj.serialize()
    elif isinstance(obj, Row):
        return dict(obj._mapping)
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, OrderedDict):
        return dict(obj)
    raise TypeError

def json_dumps(obj):
    return orjson.dumps(
        obj,
        default=default,
        option=orjson.OPT_UTC_Z | orjson.OPT_NAIVE_UTC,
    ).decode('utf-8')

def json_loads(s):
    return orjson.loads(s.decode() if isinstance(s, bytes) else s)