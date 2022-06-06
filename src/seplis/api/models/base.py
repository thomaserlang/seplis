from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, orm
from seplis.utils import row_to_dict

class Base_model(object):

    def to_dict(self):
        return row_to_dict(self)
        
    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = orm.Session.object_session(self)
        return self._session

Base = declarative_base(cls=Base_model)
metadata_obj = MetaData()