import math
import sqlalchemy as sa
from sqlalchemy import func, orm, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from typing import Any
from seplis.utils import *
from seplis.api import exceptions
from seplis.api.base.pagination import Pagination
from ..api import schemas

class Base_query(orm.Query):
 
    def paginate(self, page=1, per_page=25) -> Pagination:
        records = self.limit(per_page).offset((page-1)*per_page).all()
        if page == 1 and len(records) < per_page:
            total = len(records)
        else:
            total = self.order_by(None).count()
 
        pagination = Pagination(
            page=page,
            per_page=per_page,
            total=total,
            records=records,
        )
        return pagination

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

def create_cursor_links(request: Request, after: str | None, before: str | None):
    url = request.url.remove_query_params(['after', 'before'])
    return schemas.Page_cursor_links(
        next=str(url.include_query_params(after=after)),
        prev=str(url.include_query_params(before=before)) if 'after=' in request.url.query else None,
    )

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


def setup_before_after_events(session):
    """Call this after setting up the `sessionmaker` to
    activate before and after insert/update events.

    Supported events in the model:
        * before_insert
        * after_insert
        * before_update
        * after_update
        * before_delete
        * after_delete
        * before_upsert
        * after_upsert

    Do not make changes to the model object in after_* events.

    Example:

    class Users(Base):
        __table_name__ = 'users'

        id = sa.Column(sa.Integer)

        def before_insert(self):
            # check something or change some fields

        def after_insert(self):
            self.save_to_cache()
    """
    def _after_flush(session, flush_context):
        for target in session.new:
            if hasattr(target, 'after_insert'): 
                target.after_insert()
            if hasattr(target, 'after_upsert'): 
                target.after_upsert()
        for target in session.dirty:
            if hasattr(target, 'after_update'):
                target.after_update()
            if hasattr(target, 'after_upsert'): 
                target.after_upsert()
        for target in session.deleted:
            if hasattr(target, 'after_delete'):
                target.after_delete()

    def _before_flush(session, flush_context, instances):
        for target in session.new:
            if hasattr(target, 'before_insert'): 
                target.before_insert()
            if hasattr(target, 'before_upsert'): 
                target.before_upsert()
        for target in session.dirty:
            if hasattr(target, 'before_update'):
                target.before_update()
            if hasattr(target, 'before_upsert'): 
                target.before_upsert()
        for target in session.deleted:
            if hasattr(target, 'before_delete'):
                target.before_delete()

    sa.event.listen(session, 'before_flush', _before_flush)
    sa.event.listen(session, 'after_flush', _after_flush)