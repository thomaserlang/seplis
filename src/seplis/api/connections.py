import redis
import logging
from tornado.httpclient import AsyncHTTPClient, HTTPError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm, event
from sqlalchemy.ext.declarative import declarative_base
from seplis import config, utils
from seplis.api import exceptions
from elasticsearch import Elasticsearch, helpers
from rq import Queue

class Database:
    def __init__(self):
        self.engine = create_engine(
            config['api']['database'],
            convert_unicode=True,
            echo=False,
            pool_recycle=3599,
            encoding='UTF-8',
            connect_args={'charset': 'utf8mb4'},
        )
        self.session = sessionmaker(
            bind=self.engine,
        )
        setup_event_listeners(self.session)

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

    async def es_get(self, url, query={}, body={}):
        http_client = AsyncHTTPClient()         
        if not url.startswith('/'):
            url = '/'+url
        for arg in query:
            if not isinstance(query[arg], list):
                query[arg] = [query[arg]]
        try:
            response = await http_client.fetch(
                'http://{}{}?{}'.format(
                    config['api']['elasticsearch'],
                    url,
                    utils.url_encode_tornado_arguments(query) \
                        if query else '',
                ),
                method='POST' if body else 'GET',
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

def _after_commit(session):
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

def _after_flush(session, flush_context):
    for target in session.new:
        if hasattr(target, 'after_insert'): 
            target.after_insert()
        if hasattr(target, 'after_upsert'): 
            target.after_upsert()
    for target in session.dirty:
        if hasattr(target, 'after_update'):
            target.after_update()
        if hasattr(target, 'after_upsert'): 
            target.after_upsert()
    for target in session.deleted:
        if hasattr(target, 'after_delete'):
            target.after_delete()

def _before_flush(session, flush_context, instances):
    for target in session.new:
        if hasattr(target, 'before_insert'): 
            target.before_insert()
        if hasattr(target, 'before_upsert'): 
            target.before_upsert()
    for target in session.dirty:
        if hasattr(target, 'before_update'):
            target.before_update()
        if hasattr(target, 'before_upsert'): 
            target.before_upsert()
    for target in session.deleted:
        if hasattr(target, 'before_delete'):
            target.before_delete()
        
def setup_event_listeners(session):
    event.listen(session, 'after_commit', _after_commit)
    event.listen(session, 'before_flush', _before_flush)
    event.listen(session, 'after_flush', _after_flush)

database = Database()