from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from seplis.api.database import database
from seplis.api.main import app


@pytest_asyncio.fixture(scope='function')  # type: ignore
async def client() -> AsyncGenerator[AsyncClient]:
    await database.setup_test()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac
    await database.close_test()


@pytest_asyncio.fixture(scope='function')  # type: ignore
async def db() -> AsyncGenerator[None]:
    await database.setup_test()
    yield
    await database.close_test()
