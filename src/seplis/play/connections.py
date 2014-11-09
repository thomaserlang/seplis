from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from seplis.config import config

class Database:
    def __init__(self):
        self.engine = create_engine(
            config['play']['database'],
            convert_unicode=True,
            echo=False,
            pool_recycle=3600,
            encoding='UTF-8',
            connect_args={'charset': 'utf8'},
        )
        self.session = sessionmaker(
            bind=self.engine,
        )

database = Database()