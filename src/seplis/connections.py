import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from seplis.config import config
from elasticsearch import Elasticsearch

class Database:
    def __init__(self):
        self.engine = create_engine(
            config['database']['url'],
            convert_unicode=True,
            echo=False,
            pool_recycle=3600,
        )
        self.session = sessionmaker(
            bind=self.engine,
        )
        self.redis = redis.StrictRedis(
            config['redis']['ip'], 
            port=config['redis']['port'], 
            db=0,
            decode_responses=True,
        )
        self.es = Elasticsearch(
            config['elasticsearch'],
        )

database = Database()