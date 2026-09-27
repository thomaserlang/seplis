import asyncio
import re
from typing import Any, cast
from uuid import uuid4

from seplis import config, logger, utils
from seplis.api.database import database

from .search_index_actions import (
    apply_changes,
    create_collection,
    index_lock,
    redis_key,
    request,
)


async def rebuild_search() -> None:
    from seplis.api.movie import rebuild_movies
    from seplis.api.series import rebuild_series

    alias = config.api.typesense.collection
    name = f'{alias}_{uuid4().hex}'
    # A hard deadline leaves room to clean up before the rebuild lease expires.
    async with database.redis.lock(
        redis_key('rebuild'), timeout=3660, blocking_timeout=1
    ):
        try:
            async with asyncio.timeout(3600):
                await remove_old_collections(alias)
                async with index_lock():
                    await create_collection(name)
                    await database.redis.delete(redis_key('changes'))
                    await database.redis.set(redis_key('building'), name)
                logger.info('Building search collection {}', name)
                await rebuild_movies(collection=name)
                await rebuild_series(collection=name)
                await finish_rebuild(name)
        finally:
            async with index_lock():
                if await database.redis.get(redis_key('building')) == name:
                    await database.redis.delete(
                        redis_key('building'), redis_key('changes')
                    )
        logger.info('Search rebuild complete: {}', name)


async def remove_old_collections(alias: str) -> None:
    # Free abandoned/previous builds before allocating another full index.
    active = (await request('GET', f'/aliases/{alias}')).json()['collection_name']
    collections = (await request('GET', '/collections')).json()
    for collection in collections:
        name = collection['name']
        if name != active and re.fullmatch(re.escape(alias) + r'_[0-9a-f]{32}', name):
            await request('DELETE', f'/collections/{name}')


async def finish_rebuild(name: str) -> None:
    alias = config.api.typesense.collection
    while True:
        async with index_lock():
            if await database.redis.get(redis_key('building')) != name:
                raise RuntimeError('Search rebuild journal was lost; rebuild again')
            changes = await database.redis.execute_command(
                'HRANDFIELD', redis_key('changes'), 100, 'WITHVALUES'
            )
            if not changes:
                await request('PUT', f'/aliases/{alias}', json={'collection_name': name})
                await database.redis.delete(redis_key('building'))
                return
            latest = {
                key: utils.json_loads(value)
                for key, value in zip(changes[::2], changes[1::2], strict=True)
            }
            await apply_changes(name, latest)
            await cast(Any, database.redis.hdel(redis_key('changes'), *latest))
