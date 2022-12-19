import httpx
import tempfile
import os
import gzip
from typing import Literal, AsyncIterator
from datetime import datetime, timezone, timedelta
from seplis import logger, utils
from aiofile import async_open
from pydantic import BaseModel

client = httpx.AsyncClient()

class Id_data(BaseModel):
    id: int
    original_title: str
    popularity: float
    adult: bool
    video: bool


async def get_ids(export: Literal['movie_ids', 'tv_series_ids']) -> AsyncIterator[Id_data]:
    url = await _get_url(export=export)
    if not url:
        return
    tmp = os.path.join(tempfile.mkdtemp('seplis'), 'data.gz')
    try:
        async with client.stream('GET', url) as r:
            async with async_open(tmp, 'wb') as f:
                async for chunk in r.aiter_bytes():
                    await f.write(chunk)
        with gzip.open(tmp) as f:
            for line in f:
                yield Id_data.parse_obj(utils.json_loads(line))
    finally:
        os.remove(tmp)


async def _get_url(export):
    dts = [
        datetime.now(tz=timezone.utc).strftime('%m_%d_%Y'),
        (datetime.now(tz=timezone.utc)-timedelta(days=1)).strftime('%m_%d_%Y'),
    ]
    for dt in dts:
        url = f'http://files.tmdb.org/p/exports/{export}_{dt}.json.gz'
        r = await client.head(url)
        if r.status_code == 200:
            return url