import functools
import os
from collections.abc import Callable
from warnings import filterwarnings

import redis.asyncio as redis
from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from elasticsearch import AsyncElasticsearch
from redis.asyncio.sentinel import Sentinel
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from seplis import config, utils

filterwarnings('ignore', module=r'aiomysql')


class Database:
    def __init__(self) -> None:
        self.engine: AsyncEngine
        self.session: async_sessionmaker[AsyncSession]
        self.redis: redis.Redis | redis.RedisCluster
        self.redis_queue: ArqRedis
        self.es: AsyncElasticsearch
        self._test_setup: bool = False
        self._conn: AsyncConnection

    async def setup(self) -> None:
        self.engine = create_async_engine(
            config.api.database.replace('mysqldb', 'aiomysql').replace(
                'pymysql', 'aiomysql'
            ),
            echo=False,
            pool_pre_ping=True,
            json_serializer=lambda obj: utils.json_dumps(obj),
            json_deserializer=lambda s: utils.json_loads(s),
        )
        self.session = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        auth: tuple[str, str] | None = (
            (config.api.elasticsearch.user, config.api.elasticsearch.password)
            if config.api.elasticsearch.user and config.api.elasticsearch.password
            else None
        )
        self.es = AsyncElasticsearch(
            hosts=config.api.elasticsearch.host,
            basic_auth=auth,
            verify_certs=config.api.elasticsearch.verify_certs,
        )

        if config.api.redis.sentinel:
            sentinel = Sentinel(
                sentinels=config.api.redis.sentinel,
                password=config.api.redis.password,
                db=config.api.redis.db,
            )
            self.redis = sentinel.master_for(
                config.api.redis.master_name,
                decode_responses=True,
            )
            self.redis_queue = await create_pool(
                RedisSettings(
                    host=config.api.redis.sentinel,
                    sentinel=True,
                    sentinel_master=config.api.redis.master_name,
                    password=config.api.redis.password,
                    database=config.api.redis.db,
                ),
                default_queue_name=config.api.redis.queue_name,
            )
        else:
            self.redis = redis.Redis(
                host=config.api.redis.host,
                port=config.api.redis.port,
                password=config.api.redis.password,
                db=config.api.redis.db,
                decode_responses=True,
            )
            self.redis_queue = await create_pool(
                RedisSettings(
                    host=config.api.redis.host,
                    port=config.api.redis.port,
                    password=config.api.redis.password,
                    database=config.api.redis.db,
                ),
                default_queue_name=config.api.redis.queue_name,
            )

    async def setup_test(self) -> None:
        config.api.database = config.api.database_test
        config.api.redis.db = 15
        config.api.elasticsearch.index_prefix = 'seplis_test_'
        if not self._test_setup:
            from sqlalchemy.engine import url

            u = url.make_url(config.api.database_test)
            db = u.database
            u = url.URL.create(
                drivername=u.drivername,
                username=u.username,
                password=u.password,
                host=u.host,
                port=u.port,
            )
            engine = create_engine(u)
            with engine.begin() as conn:
                conn.execute(
                    text(
                        f'CREATE SCHEMA IF NOT EXISTS {db} DEFAULT CHARACTER SET utf8mb4;'
                    )
                )
            from alembic import command
            from alembic.config import Config

            cfg = Config(os.path.dirname(os.path.abspath(__file__)) + '/alembic.ini')
            cfg.set_main_option('script_location', 'seplis.api:migration')
            cfg.set_main_option('sqlalchemy.url', config.api.database_test)
            command.upgrade(cfg, 'head')

        await self.setup()
        self._conn = await self.engine.connect()
        self.session = async_sessionmaker(
            self._conn, expire_on_commit=False, class_=AsyncSession
        )

        self._test_setup = True
        self.trans = await self._conn.begin()

        await self.redis.flushdb()

    async def close(self) -> None:
        await self.engine.dispose()
        await self.redis.close()
        await self.redis_queue.close()
        await self.es.close()

    async def close_test(self) -> None:
        await self.trans.rollback()
        await self._conn.close()
        await self.close()


database = Database()


def auto_session[**P, R](method: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(method)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if kwargs.get('session'):
            return await method(*args, **kwargs)  # type: ignore[return-value]
        async with database.session() as session:
            kwargs['session'] = session
            result = await method(*args, **kwargs)  # type: ignore[misc]
            await session.commit()
            return result

    return wrapper  # type: ignore[return-value]
