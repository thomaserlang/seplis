import redis.asyncio as redis
import os
from redis.asyncio.sentinel import Sentinel

from arq import create_pool, ArqRedis
from arq.connections import RedisSettings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from elasticsearch import AsyncElasticsearch
from seplis import config, utils, logger

class Database:
    
    def __init__(self):
        self.engine: AsyncEngine = None
        self.session: sessionmaker = None
        self.es: AsyncElasticsearch = None
        self.redis: redis.Redis = None
        self.redis_queue: ArqRedis = None
        self._test_setup = False
        self._conn = None

    async def setup(self):
        self.engine = create_async_engine(
            config.data.api.database.replace('mysqldb', 'aiomysql').replace('pymysql', 'aiomysql'),
            echo=False,
            pool_pre_ping=True,
            json_serializer=lambda obj: utils.json_dumps(obj),
            json_deserializer=lambda s: utils.json_loads(s),
        )
        self.session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

        auth = (config.data.api.elasticsearch.user, config.data.api.elasticsearch.password) \
            if config.data.api.elasticsearch.user and config.data.api.elasticsearch.password else None
        self.es = AsyncElasticsearch(
            hosts=config.data.api.elasticsearch.host, 
            basic_auth=auth, 
            verify_certs=config.data.api.elasticsearch.verify_certs,
        ) 

        if config.data.api.redis.sentinel:
            sentinel = Sentinel(
                sentinels=config.data.api.redis.sentinel,
                password=config.data.api.redis.password,
                db=config.data.api.redis.db,
            )
            self.redis = sentinel.master_for(
                config.data.api.redis.master_name,
                decode_responses=True,
            )
            self.redis_queue = await create_pool(RedisSettings(
                host=config.data.api.redis.sentinel,
                sentinel=True,
                sentinel_master=config.data.api.redis.master_name,
                password=config.data.api.redis.password,
                database=config.data.api.redis.db,
            ), default_queue_name=config.data.api.redis.queue_name)
        else:
            self.redis = redis.Redis(
                host=config.data.api.redis.host,
                port=config.data.api.redis.port,
                password=config.data.api.redis.password,
                db=config.data.api.redis.db,
                decode_responses=True,
            )
            self.redis_queue = await create_pool(RedisSettings(
                host=config.data.api.redis.host,
                port=config.data.api.redis.port,
                password=config.data.api.redis.password,
                database=config.data.api.redis.db,
            ), default_queue_name=config.data.api.redis.queue_name)

    async def setup_test(self):
        config.data.api.database = config.data.api.database_test
        config.data.api.redis.db = 15
        config.data.api.elasticsearch.index_prefix = 'seplis_test_'
        if not self._test_setup:
            from sqlalchemy.engine import url
            u = url.make_url(config.data.api.database_test)
            db = u.database
            u = url.URL.create(
                drivername=u.drivername,
                username=u.username,
                password=u.password,
                host=u.host,
                port=u.port,
            )
            engine = create_engine(u)
            engine.execute(text(f'CREATE SCHEMA IF NOT EXISTS {db} DEFAULT CHARACTER SET utf8mb4;'))
            engine.dispose()
            from alembic.config import Config
            from alembic import command
            cfg = Config(os.path.dirname(os.path.abspath(__file__))+'/alembic.ini')
            cfg.set_main_option('script_location', 'seplis.api:migration')
            cfg.set_main_option('sqlalchemy.url', config.data.api.database_test)
            command.upgrade(cfg, 'head')

        await self.setup()
        self._conn = await self.engine.connect()
        self.session = sessionmaker(self._conn, expire_on_commit=False, class_=AsyncSession)

        self._test_setup = True
        self.trans = await self._conn.begin()

        await self.redis.flushdb()
        from seplis.api import elasticcreate
        await elasticcreate.create_indices(self.es)

    async def close(self):
        await self.engine.dispose()
        await self.redis.close()
        await self.redis_queue.close()
        await self.es.close()

    async def close_test(self):
        await self.trans.rollback()
        await self._conn.close()
        await self.close()

database = Database()