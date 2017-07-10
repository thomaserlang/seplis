from seplis.utils import *
from seplis.api import exceptions
from seplis.api.base.pagination import Pagination

import sqlalchemy as sa
from sqlalchemy import orm

class Base_query(orm.Query):
 
    def paginate(self, page=1, per_page=25):
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