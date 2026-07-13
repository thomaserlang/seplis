import gzip
import os
import tempfile
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import httpx
from aiofile import async_open

from seplis import utils


@dataclass(slots=True, kw_only=True)
class IdData:
    id: int
    original_title: str
    popularity: float
    adult: bool | None = None
    video: bool | None = None


async def get_ids(
    export: Literal['movie_ids', 'tv_series_ids'],
) -> AsyncIterator[IdData]:
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
                    yield id_data_mapper(utils.json_loads(line))
    finally:
        os.remove(tmp)


async def _get_url(export: Literal['movie_ids', 'tv_series_ids']) -> str | None:
    dts = [
        datetime.now(tz=UTC).strftime('%m_%d_%Y'),
        (datetime.now(tz=UTC) - timedelta(days=1)).strftime('%m_%d_%Y'),
    ]
    for dt in dts:
        url = f'http://files.tmdb.org/p/exports/{export}_{dt}.json.gz'
        async with httpx.AsyncClient() as client:
            r = await client.head(url)
            if r.status_code == 200:
                return url
    return None


def id_data_mapper(data: dict[str, Any]) -> IdData:
    return IdData(
        id=int(data['id']),
        original_title=data.get('original_title') or data.get('original_name') or '',
        popularity=float(data.get('popularity') or 0),
        adult=data.get('adult'),
        video=data.get('video'),
    )
