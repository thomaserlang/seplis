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
        database_url = database_url or config['api']['database']
        redis_db = redis_db or config['api']['redis']['db']
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_recycle=3599,
            pool_pre_ping=True,
            connect_args={
                'read_timeout': config['api']['database_read_timeout'],
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

        if config['api']['redis']['sentinel']:
            sentinel = redis.Sentinel(
                config['api']['redis']['sentinel'], 
                socket_timeout=0.1, 
                db=config['api']['redis']['db'], 
                password=config['api']['redis']['password'],
            )
            self.redis = sentinel.master_for(
                config['api']['redis']['master_name'],
                decode_responses=True,
            )
            sentinel = redis.Sentinel(
                config['api']['redis']['sentinel'],
                db=redis_db, 
                password=config['api']['redis']['password'],
            )
            self.queue_redis = sentinel.master_for(config['api']['redis']['master_name'])
        else:
            self.redis = redis.StrictRedis(
                config['api']['redis']['ip'], 
                port=config['api']['redis']['port'], 
                db=config['api']['redis']['db'],
                password=config['api']['redis']['password'],
                decode_responses=True,
            )
            self.queue_redis = redis.StrictRedis(
                config['api']['redis']['ip'], 
                port=config['api']['redis']['port'], 
                db=redis_db,
                password=config['api']['redis']['password'],
            )
        self.queue = Queue(connection=self.queue_redis)
        self.es = Elasticsearch(
            config['api']['elasticsearch'],
        )
        self.es_async = AsyncElasticsearch(config['api']['elasticsearch'])
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

    async def es_get(self, url, query={}, body={}):
        http_client = AsyncHTTPClient()         
        if not url.startswith('/'):
            url = '/'+url
        for arg in query:
            if not isinstance(query[arg], list):
                query[arg] = [query[arg]]
        try:
            response = await http_client.fetch(
                '{}{}?{}'.format(
                    config['api']['elasticsearch'],
                    url,
                    utils.url_encode_tornado_arguments(query) \
                        if query else '',
                    connect_timeout=2.0,
                    request_timeout=2.0,
                ),
                method='POST' if body else 'GET',
                headers={
                    'Content-Type': 'application/json',
                },
                body=utils.json_dumps(body) if body else None,
            )
            return utils.json_loads(response.body)
        except HTTPError as e:
            try:
                extra = utils.json_loads(e.response.body)
                if e.code == 404:
                    return extra
            except:
                extra = {'error': e.response.body.decode('utf-8')}
            raise exceptions.Elasticsearch_exception(
                e.code,
                extra,
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