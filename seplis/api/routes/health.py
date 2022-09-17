import asyncio
from fastapi import APIRouter, Response
from pydantic import BaseModel
from seplis.api.database import database

router = APIRouter()

class Health_response(BaseModel):
    error: bool
    message: str
    service: str

@router.get('/health', response_model=list[Health_response])
async def check_health(response: Response):
    result = await asyncio.gather(
        db_check(),
        redis_check(),
        elasticsearch_check(),
    )
    if any([r.error for r in result]):
        response.status_code = 500
    return result

async def db_check() -> Health_response:
    r = Health_response(
        error=False,
        message='OK',
        service='Database',
    )
    try:
        async with database.session() as s:
            await s.execute('SELECT 1')
    except Exception as e:
        r.error = True
        r.message = f'Error: {str(e)}'
    return r

async def redis_check() -> Health_response:
    r = Health_response(
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

async def elasticsearch_check() -> Health_response:
    r = Health_response(
        error=False,
        message='OK',
        service='Elasticsearch',
    )
    p = await database.es.ping()
    if not p:
        r.error = True
        r.message = 'Unable to connect'
    return r