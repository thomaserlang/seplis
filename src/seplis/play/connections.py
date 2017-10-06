from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from seplis.config import config
import os.path
import alembic.config
from alembic import command, context

def get_config():
    cfg = alembic.config.Config(
        os.path.dirname(
            os.path.abspath(__file__)
        )+'/alembic.ini'
    )
    cfg.set_main_option('script_location', 'seplis.play:migration')
    cfg.set_main_option('url', config['play']['database'])
    return cfg

def upgrade():
    cfg = get_config()
    command.upgrade(cfg, 'head')

class Database:
    def __init__(self):
        self.engine = create_engine(
            config['play']['database'],
            convert_unicode=True,
            echo=False,
            pool_recycle=3600,
            encoding='UTF-8',
            connect_args={'charset': 'utf8mb4'},
        )
        self.session = sessionmaker(
            bind=self.engine,
        )

database = Database()