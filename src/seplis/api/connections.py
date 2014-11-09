import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from seplis.config import config
from elasticsearch import Elasticsearch
from rq import Queue

class Database:
    def __init__(self):
        self.engine = create_engine(
            config['api']['database'],
            convert_unicode=True,
            echo=False,
            pool_recycle=3600,
            encoding='UTF-8',
            connect_args={'charset': 'utf8'},
        )
        self.session = sessionmaker(
            bind=self.engine,
        )
        self.redis = redis.StrictRedis(
            config['api']['redis']['ip'], 
            port=config['api']['redis']['port'], 
            db=0,
            decode_responses=True,
        )
        self.queue_redis = redis.StrictRedis(
            config['api']['redis']['ip'], 
            port=config['api']['redis']['port'], 
            db=1,
        )
        self.queue = Queue(connection=self.queue_redis)
        self.es = Elasticsearch(
            config['api']['elasticsearch'],
        )

database = Database()