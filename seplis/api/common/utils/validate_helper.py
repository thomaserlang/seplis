from functools import cache
from typing import Any

from pydantic import TypeAdapter


@cache
def get_adapter(type_: type[Any]) -> TypeAdapter[Any]:
    return TypeAdapter(type_)


def validate_python[T](type_: type[T], value: Any) -> T:
    return get_adapter(type_).validate_python(value)


def validate_json[T](type_: type[T], data: str | bytes | bytearray) -> T:
    return get_adapter(type_).validate_json(data)
