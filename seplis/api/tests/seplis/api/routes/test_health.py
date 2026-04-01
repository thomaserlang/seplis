import pytest

from seplis.api.testbase import AsyncClient, run_file


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    r = await client.get('/health')
    assert r.status_code == 200, r.content


if __name__ == '__main__':
    run_file(__file__)