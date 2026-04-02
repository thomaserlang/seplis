import base64
from datetime import UTC, datetime
from typing import Any

import sqlalchemy as sa
from sqlakeyset.asyncio import select_page
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import DateTime, TypeDecorator


async def paginate_cursor(
    session: AsyncSession,
    query: Any,
    page_query: Any,
    backwards=False,
):
    from ..api import schemas

    page = await select_page(
        s=session,
        selectable=query,
        per_page=page_query.per_page,
        page=base64.urlsafe_b64decode(page_query.cursor).decode()
        if page_query.cursor
        else None,
    )
    cursor = (
        base64.urlsafe_b64encode(page.paging.bookmark_next.encode()).decode()
        if page.paging.has_next
        else None
    )
    return schemas.Page_cursor_result(
        items=page.paging.rows,
        cursor=cursor,
    )


async def paginate_cursor_total(
    session: AsyncSession,
    query: Any,
    page_query: Any,
    backwards=False,
):
    from ..api import schemas

    count_subquery = query.order_by(None).options(sa.orm.noload('*')).subquery()
    p = await paginate_cursor(session, query, page_query, backwards)
    total = await session.scalar(
        sa.select(sa.func.count(sa.literal_column('*'))).select_from(count_subquery)
    )
    return schemas.Page_cursor_total_result(
        items=p.items,
        cursor=p.cursor,
        total=total,
    )


class UUID(sa.types.UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw) -> str:
        return 'UUID'

    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                value = str(value)
            return value

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                value = str(value)
            return value

        return process


class UtcDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError('expected datetime.datetime, not ' + repr(value))
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            else:
                value = value.astimezone(UTC)
            return value
        return None

    def process_result_value(self, value, dialect):
        if value is not None and isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            else:
                value = value.astimezone(UTC)
        return value
