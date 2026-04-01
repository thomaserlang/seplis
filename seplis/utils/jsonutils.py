import decimal
from collections import OrderedDict
from typing import Any

import orjson
from pydantic import BaseModel
from sqlalchemy.engine import Row


def default(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, set):
        return list(obj)
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    if hasattr(obj, 'serialize'):
        return obj.serialize()
    if isinstance(obj, Row):
        return dict(obj._mapping)
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, OrderedDict):
        return dict(obj)
    raise TypeError


def json_dumps(obj: Any) -> str:
    return orjson.dumps(
        obj,
        default=default,
        option=orjson.OPT_UTC_Z | orjson.OPT_NAIVE_UTC,
    ).decode('utf-8')


def json_loads(s: str | bytes) -> Any:
    return orjson.loads(s.decode() if isinstance(s, bytes) else s)
