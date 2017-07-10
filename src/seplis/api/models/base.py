from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event, orm
from seplis.api.base.pagination import Pagination
Base = declarative_base()

@property
def session(self):
    if not hasattr(self, '_session'):
        self._session = orm.Session.object_session(self)
    return self._session

Base.session = session