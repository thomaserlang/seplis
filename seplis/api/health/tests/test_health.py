import pytest
from httpx import ASGITransport, AsyncClient

from seplis.api.main import app
from seplis.api.testbase import run_file


@pytest.mark.asyncio
async def test_health() -> None:
    # No service setup: the endpoint only checks that the API can respond.
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        r = await client.get('/health')
    assert r.status_code == 200, r.content
    assert r.json() == {'status': 'ok'}


if __name__ == '__main__':
    run_file(__file__)
