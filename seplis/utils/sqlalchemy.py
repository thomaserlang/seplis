import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import DateTime, TypeDecorator
from datetime import datetime, timezone
from typing import Any
from ..api import schemas
from uuid6 import uuid7
from .sqlakeyset.paging import get_page
from .sqlakeyset.results import unserialize_bookmark
from .. import logger


async def paginate_cursor(session: AsyncSession, query: Any, page_query: schemas.Page_cursor_query, backwards=False):
    place = None
    if page_query.cursor:
        place, backwards = unserialize_bookmark(page_query.cursor)
    page = await get_page(
        db=session, 
        selectable=query, 
        per_page=page_query.per_page, 
        place=place, 
        backwards=backwards,
    )
    return schemas.Page_cursor_result(
        items=page.paging.rows,
        cursor=page.paging.bookmark_next if page.paging.has_next else None,
    )


async def paginate_cursor_total(session: AsyncSession, query: Any, page_query: schemas.Page_cursor_query, backwards=False):
    count_subquery = query.order_by(None).options(sa.orm.noload("*")).subquery()
    p = await paginate_cursor(session, query, page_query, backwards)
    total = await session.scalar(sa.select(sa.func.count(sa.literal_column("*"))).select_from(count_subquery))
    return schemas.Page_cursor_total_result(
        items=p.items,
        cursor=p.cursor,
        total=total,
    )


class UUID(sa.types.UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "UUID"

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


def uuid7_mariadb():
    '''
    Since the MariaDB UUID data type reorderes the stored UUID to be more index friendly
    for UUIDv1 (nnnnnnnnnnnn-vsss-Vhhh-mmmm-llllllll), we have to reorder the UUIDv7
    https://mariadb.com/kb/en/uuid-data-type/
    '''
    a = str(uuid7())
    return f'{a[24:32]}-{a[32:36]}-{a[19:23]}-{a[14:18]}-{a[0:8]}{a[9:13]}'


class UtcDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError('expected datetime.datetime, not ' +
                                repr(value))
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
            return value

    def process_result_value(self, value, dialect):
        if value is not None and isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
        return value