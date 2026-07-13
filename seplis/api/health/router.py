import asyncio
from dataclasses import dataclass

import sqlalchemy as sa
from fastapi import APIRouter, Response

from seplis.api.database import database

router = APIRouter(prefix='/health', tags=['Health'])


@dataclass(slots=True, kw_only=True)
class HealthResponse:
    error: bool
    message: str
    service: str


@router.get('')
async def check_health(response: Response) -> list[HealthResponse]:
    result = await asyncio.gather(
        db_check(),
        redis_check(),
        elasticsearch_check(),
    )
    if any([r.error for r in result]):
        response.status_code = 500
    return list(result)


async def db_check() -> HealthResponse:
    r = HealthResponse(
        error=False,
        message='OK',
        service='Database',
    )
    try:
        async with database.session() as s:
            await s.execute(sa.text('SELECT 1'))
    except Exception as e:
        r.error = True
        r.message = f'Error: {str(e)}'
    return r


async def redis_check() -> HealthResponse:
    r = HealthResponse(
        error=False,
        message='OK',
        service='Redis',
    )
    try:
        await database.redis.ping()
    except Exception as e:
        r.error = True
        r.message = f'Error: {str(e)}'
    return r


async def elasticsearch_check() -> HealthResponse:
    r = HealthResponse(
        error=False,
        message='OK',
        service='Elasticsearch',
    )
    p = await database.es.ping()
    if not p:
        r.error = True
        r.message = 'Unable to connect'
    return r
