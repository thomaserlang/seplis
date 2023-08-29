import httpx
import tempfile
import os
import gzip
from typing import Literal, AsyncIterator
from datetime import datetime, timezone, timedelta
from seplis import logger, utils
from aiofile import async_open
from pydantic import BaseModel, ConfigDict, Field


class Id_data(BaseModel):
    id: int
    original_title: str = Field(alias='original_name')
    popularity: float
    adult: bool = None
    video: bool = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


async def get_ids(export: Literal['movie_ids', 'tv_series_ids']) -> AsyncIterator[Id_data]:
    url = await _get_url(export=export)
    if not url:
        return
    tmp = os.path.join(tempfile.mkdtemp('seplis'), 'data.gz')
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url) as r:
                async with async_open(tmp, 'wb') as f:
                    async for chunk in r.aiter_bytes():
                        await f.write(chunk)
            with gzip.open(tmp) as f:
                for line in f:
                    yield Id_data.model_validate(utils.json_loads(line))
    finally:
        os.remove(tmp)


async def _get_url(export):
    dts = [
        datetime.now(tz=timezone.utc).strftime('%m_%d_%Y'),
        (datetime.now(tz=timezone.utc)-timedelta(days=1)).strftime('%m_%d_%Y'),
    ]
    for dt in dts:
        url = f'http://files.tmdb.org/p/exports/{export}_{dt}.json.gz'
        async with httpx.AsyncClient() as client:
            r = await client.head(url)
            if r.status_code == 200:
                return url