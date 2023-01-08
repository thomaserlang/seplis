import pytest
from seplis.api.testbase import client, run_file, AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    r = await client.get('/health')
    assert r.status_code == 200, r.content


if __name__ == '__main__':
    run_file(__file__)