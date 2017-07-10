from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
Base = declarative_base()

def add_session_prop_to_models():
    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = orm.Session.object_session(self)
        return self._session
    Base.session = session
add_session_prop_to_models()