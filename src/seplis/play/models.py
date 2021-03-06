import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from seplis import utils

base = declarative_base()

class JSONEncodedDict(sa.TypeDecorator):  
    impl = sa.Text  
  
    def process_bind_param(self, value, dialect):
        if value is None:  
            return None
        if isinstance(value, str):
            return value
        return utils.json_dumps(value)
  
    def process_result_value(self, value, dialect):  
        if not value:  
            return None
        return utils.json_loads(value)  

class Episode(base):
    __tablename__ = 'episodes'

    show_id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.Text)
    meta_data = sa.Column(JSONEncodedDict())
    modified_time = sa.Column(sa.DateTime)

class Episode_number_lookup(base):
    __tablename__ = 'episode_number_lookup'    

    show_id = sa.Column(sa.Integer, primary_key=True)
    lookup_type = sa.Column(sa.Integer, primary_key=True)
    lookup_value = sa.Column(sa.String(45), primary_key=True)
    number = sa.Column(sa.Integer)

class Show_id_lookup(base):
    __tablename__ = 'show_id_lookup'

    file_show_title = sa.Column(sa.String(200), primary_key=True)
    show_title = sa.Column(sa.String(200))
    show_id = sa.Column(sa.Integer)
    updated = sa.Column(sa.DateTime)