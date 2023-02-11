from base64 import urlsafe_b64decode, urlsafe_b64encode
import math
import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from typing import Any
from seplis.utils import *
from seplis.api import exceptions
from ..api import schemas
from uuid6 import uuid7


async def paginate(session: AsyncSession, query: Any, page_query: schemas.Page_query, request: Request, scalars: bool = True) -> schemas.Page_result:
    limited = query.limit(page_query.per_page).offset((page_query.page-1)*page_query.per_page)
    if scalars:
        items = await session.scalars(limited)
    else:
        items = await session.execute(limited)
    items = items.all()
    if page_query.page == 1 and len(items) < page_query.per_page:
        total = len(items)
    else:
        total = await session.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    page = schemas.Page_result(
        page=page_query.page,
        per_page=page_query.per_page,
        total=total,
        items=items,
        pages=int(math.ceil(float(total) / page_query.per_page))
    )
    page.links = create_page_links(request=request, page=page)
    return page


async def paginate_cursor(session: AsyncSession, query: Any, fields: list[Any], page_cursor: schemas.Page_cursor_query):
    query = query.limit(page_cursor.first+1).order_by(*[sa.asc(field) for field in fields])
    query_cursor = page_cursor.after or page_cursor.before
    if query_cursor:
        cursor_list = urlsafe_b64decode(query_cursor.encode()).decode().split(',')
        if page_cursor.after:
            query = query.where(sa.tuple_(*fields) > sa.tuple_(*cursor_list))
        else:
            query = query.where(sa.tuple_(*fields) < sa.tuple_(*cursor_list))

    items = await session.scalars(query)
    items = items.all()

    cursor: str | None = None
    if len(items) > page_cursor.first:
        items = items[:-1]
        cursor = urlsafe_b64encode(','.join([str(getattr(items[-1], f.key)) for f in fields]).encode()).decode()
        
    page = schemas.Page_cursor_result(
        items=items,
        cursor=cursor,
    )
    return page


def create_page_links(request: Request, page: schemas.Page_result):
    url = request.url
    return schemas.Page_links(
        first=str(url.include_query_params(page=1)),
        next=str(url.include_query_params(page=page.page+1)) if page.page < page.pages else None,
        prev=str(url.include_query_params(page=page.page-1)) if page.page > 1 else None,
        last=str(url.include_query_params(page=page.pages)) if page.pages > 1 else None 
    )


def sort_parser(sort, sort_lookup, sort_list=None):
    """
    Parses a list of string sort types to SQLAlchemy field sorts.

    Example:

        sort_lookup = {
            'journal_entry_id': models.Journal_entry.id,
            'patient': {
                'first_name': models.Patient.first_name,
            }
        }

        sort = sort_parser(
            'patient.first_name, -journal_entry_id',
            sort_lookup
        )

        session.query(
            models.Patient,
            models.Journal_entry,
        ).order_by(
            *sort
        )

    :param sort: [`str`]
    :param sort_lookup: [`SQLAlchemy model field`]
    :returns: [`SQLAlchemy model sort field`]
    """
    if sort_list == None:
        sort_list = []
    sort = filter(None, sort.split(','))
    for s in sort:
        if '.' in s:
            sub = s.split('.', 1)
            key = sub[0]
            if not isinstance(sort_lookup[key], dict):
                continue
            if len(sub) == 2:
                sort_parser(sub[1], sort_lookup[key], sort_list)
            continue
        sort_type = sa.asc
        s = s.strip()
        if s.endswith(':desc'):
            sort_type = sa.desc
            s = s[:-5]
        elif s.endswith(':asc'):
            s = s[:-4]
        if s not in sort_lookup or isinstance(sort_lookup[s], dict):
            raise exceptions.Sort_not_allowed(s)
        sort_list.append(
            sort_type(
                sort_lookup[s]
            )
        )
    return sort_list


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