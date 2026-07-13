from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import DateTime, TypeDecorator


class UUID(sa.types.UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw: Any) -> str:
        return 'UUID'

    def bind_processor(  # ty: ignore[invalid-method-override]
        self, dialect: Dialect
    ) -> Callable[[Any], str | None]:
        def process(value: Any) -> str | None:
            if value is not None:
                value = str(value)
            return value

        return process

    def result_processor(  # ty: ignore[invalid-method-override]
        self, dialect: Dialect, coltype: Any
    ) -> Callable[[Any], str | None]:
        def process(value: Any) -> str | None:
            if value is not None:
                value = str(value)
            return value

        return process


class UtcDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Dialect) -> datetime | None:
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError('expected datetime.datetime, not ' + repr(value))
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            else:
                value = value.astimezone(UTC)
            return value
        return None

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is not None and isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            else:
                value = value.astimezone(UTC)
        return value
