from collections.abc import AsyncGenerator

import pytest_asyncio
import respx
from httpx import ASGITransport, AsyncClient

from seplis import config
from seplis.api.database import database
from seplis.api.main import app


@pytest_asyncio.fixture(scope='function')
async def client(respx_mock: respx.MockRouter) -> AsyncGenerator[AsyncClient]:
    respx_mock.route(url__startswith=config.api.typesense.host).pass_through()
    await database.setup_test()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac
    await database.close_test()


@pytest_asyncio.fixture(scope='function')
async def db() -> AsyncGenerator[None]:
    await database.setup_test()
    yield
    await database.close_test()
