import asyncio
import redis
import logging
from tornado.httpclient import AsyncHTTPClient, HTTPError
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm, event
from seplis import config, utils
from seplis.api import exceptions
from elasticsearch import AsyncElasticsearch, Elasticsearch, helpers
from rq import Queue

class Database:

    def connect(self, database_url=None, redis_db=None):
        database_url = database_url or config.data.api.database
        redis_db = redis_db or config.data.api.redis.db
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_recycle=3599,
            pool_pre_ping=True,
            connect_args={
                'read_timeout': config.data.api.database_read_timeout            
            },
        )
        self.setup_sqlalchemy_session(self.engine)

        self.async_engine = create_async_engine(
            database_url.replace('mysqldb', 'aiomysql').replace('pymysql', 'aiomysql'),
            echo=False,
            pool_recycle=3599,
            pool_pre_ping=True,
            json_serializer=lambda obj: utils.json_dumps(obj),
            json_deserializer=lambda s: utils.json_loads(s),
        )
        self.setup_sqlalchemy_async_session(self.async_engine)
        
        if config.data.api.redis.sentinel:
            sentinel = redis.Sentinel(
                config.data.api.redis.sentinel, 
                socket_timeout=0.1, 
                db=redis_db,
                password=config.data.api.redis.password,
            )
            self.redis = sentinel.master_for(
                config.data.api.redis.master_name,
                decode_responses=True,
            )
            sentinel = redis.Sentinel(
                config.data.api.redis.sentinel,
                db=redis_db, 
                password=config.data.api.redis.password,
            )
            self.queue_redis = sentinel.master_for(config.data.api.redis.master_name)
        else:
            self.redis = redis.Redis(
                config.data.api.redis.ip, 
                port=config.data.api.redis.port, 
                db=redis_db,
                password=config.data.api.redis.password,
                decode_responses=True,
            )
            self.queue_redis = redis.Redis(
                config.data.api.redis.ip, 
                port=config.data.api.redis.port, 
                db=redis_db,
                password=config.data.api.redis.password,
            )
        self.queue = Queue(connection=self.queue_redis)

        auth = (config.data.api.elasticsearch.user, config.data.api.elasticsearch.password) if config.data.api.elasticsearch.user else None
        self.es = Elasticsearch(
            hosts=config.data.api.elasticsearch.host, 
            basic_auth=auth, 
            verify_certs=config.data.api.elasticsearch.verify_certs,
        )
        self.es_async = AsyncElasticsearch(
            hosts=config.data.api.elasticsearch.host, 
            basic_auth=auth, 
            verify_certs=config.data.api.elasticsearch.verify_certs,
        )    
        
    def setup_sqlalchemy_session(self, connection):
        self.session = sessionmaker(
            bind=connection,
            query_cls=utils.sqlalchemy.Base_query,
        )
        utils.sqlalchemy.setup_before_after_events(self.session)
        event.listen(self.session, 'after_commit', event_commit_es_bulk_and_pipe)

    def setup_sqlalchemy_async_session(self, connection):
        self.async_session = sessionmaker(
            bind=connection,
            expire_on_commit=False, 
            class_=AsyncSession,
        )

@property
def pipe(self):
    '''Adds a redis pipeline to the SQLAlchemy session.
    The pipeline will be lazy loaded.
    '''
    if not hasattr(self, '_pipe') or not self._pipe:
        self._pipe = database.redis.pipeline()
    return self._pipe
orm.Session.pipe = pipe

@property
def es_bulk(self):
    '''Adds elasticsearch bulk list to the session.
    The list will be lazy loaded.
    '''
    if not hasattr(self, '_es_bulk') or not self._es_bulk:
        self._es_bulk = []
    return self._es_bulk
orm.Session.es_bulk = es_bulk

def event_commit_es_bulk_and_pipe(session):
    if hasattr(session, '_pipe'):
        session.pipe.execute()
    if hasattr(session, '_es_bulk') and session._es_bulk:
        try:
            helpers.bulk(
                database.es, 
                session._es_bulk
            )
        finally:
            session._es_bulk = []

database = Database()