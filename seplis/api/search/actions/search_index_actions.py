import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast
from uuid import uuid4

import httpx

from seplis import config, utils
from seplis.api.database import database


def redis_key(suffix: str) -> str:
    return f'search:{config.api.typesense.collection}:{suffix}'


@asynccontextmanager
async def index_lock() -> AsyncIterator[None]:
    # Bound work to less than the lease; a crashed process cannot block writers.
    async with database.redis.lock(redis_key('write'), timeout=60, blocking_timeout=30):
        async with asyncio.timeout(20):
            yield


async def request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    response = await database.search.request(method, path, **kwargs)
    response.raise_for_status()
    return response


async def create_collection(name: str) -> None:
    await request(
        'POST',
        '/collections',
        json={
            'name': name,
            'fields': [
                {'name': 'title', 'type': 'string'},
                {'name': 'aliases', 'type': 'string[]'},
                {'name': 'primary_keys', 'type': 'string[]', 'facet': True},
                {'name': 'name_keys', 'type': 'string[]', 'facet': True},
                {'name': 'type', 'type': 'string', 'facet': True},
                {'name': 'year', 'type': 'int32', 'facet': True},
                {'name': 'imdb', 'type': 'string', 'facet': True},
                {'name': 'popularity', 'type': 'float'},
                {'name': 'payload', 'type': 'string', 'index': False},
            ],
            'default_sorting_field': 'popularity',
        },
    )


async def ensure_index() -> None:
    alias = config.api.typesense.collection
    async with index_lock():
        response = await database.search.get(f'/aliases/{alias}')
        if response.status_code != 404:
            response.raise_for_status()
            return
        name = f'{alias}_{uuid4().hex}'
        await create_collection(name)
        await request('PUT', f'/aliases/{alias}', json={'collection_name': name})


async def import_documents(collection: str, documents: list[dict[str, Any]]) -> None:
    if not documents:
        return
    response = await request(
        'POST',
        f'/collections/{collection}/documents/import',
        params={'action': 'upsert'},
        content='\n'.join(utils.json_dumps(d) for d in documents),
        headers={'Content-Type': 'text/plain'},
    )
    results = [utils.json_loads(line) for line in response.text.splitlines()]
    # Typesense returns HTTP 200 even when individual documents fail.
    errors = [r for r in results if not r.get('success')]
    if errors or len(results) != len(documents):
        raise RuntimeError(f'Search import failed: {errors[:3]}')


async def write_documents(documents: list[dict[str, Any]]) -> None:
    async with index_lock():
        await write_documents_locked(documents)


async def write_documents_locked(documents: list[dict[str, Any]]) -> None:
    await write_changes({d['id']: d for d in documents})


async def write_changes(changes: dict[str, dict[str, Any] | None]) -> None:
    # The caller holds index_lock for the write and rebuild bookkeeping together.
    if not changes:
        return
    if await database.redis.exists(redis_key('building')):
        await cast(
            Any,
            database.redis.hset(
                redis_key('changes'),
                mapping={key: utils.json_dumps(value) for key, value in changes.items()},
            ),
        )
    await apply_changes(config.api.typesense.collection, changes)


async def delete_document(identifier: str) -> None:
    async with index_lock():
        await write_changes({identifier: None})


async def apply_changes(
    collection: str, changes: dict[str, dict[str, Any] | None]
) -> None:
    await import_documents(collection, [d for d in changes.values() if d is not None])
    deleted = [key for key, value in changes.items() if value is None]
    if deleted:
        await request(
            'DELETE',
            f'/collections/{collection}/documents',
            params={'filter_by': f'id:=[{",".join(deleted)}]'},
        )
