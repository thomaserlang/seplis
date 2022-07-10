from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from seplis import utils
from seplis.config import config
import os.path
import alembic.config
from alembic import command

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
    def connect(self):
        self.engine = create_engine(
            config['play']['database'],
            echo=False,
            pool_recycle=3599,
            pool_pre_ping=True,
        )
        self.session = sessionmaker(
            bind=self.engine,
        )

        self.engine_async = create_async_engine(
            config['play']['database'].replace('mysqldb', 'aiomysql').replace('pymysql', 'aiomysql'),
            echo=False,
            pool_recycle=3599,
            pool_pre_ping=True,
            json_serializer=lambda obj: utils.json_dumps(obj),
            json_deserializer=lambda s: utils.json_loads(s),
        )
        self.session_async = sessionmaker(
            bind=self.engine_async,
            expire_on_commit=False, 
            class_=AsyncSession,
        )

database = Database()