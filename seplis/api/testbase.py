from typing import Any
import pytest_asyncio
from httpx import AsyncClient
from seplis import config, config_load
from seplis.api import schemas, constants, models
from seplis.api.main import app


@pytest_asyncio.fixture(scope='function')
async def client():
    from seplis.api.database import database
    config_load()
    config.data.test = True
    await database.setup_test()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    await database.close_test()


async def user_signin(client: AsyncClient, scopes: list[str] = ['me']) -> int:
    user = await models.User.save(data=schemas.User_create(
        username='testuser',
        email='test@example.com',
        password='1'*10,
    ))
    token = await models.Token.new_token(user_id=user.id, expires_days=1, scopes=scopes)
    client.headers['Authorization'] = f'Bearer {token}'
    return user.id


def parse_obj_as(type: Any, data: Any):
    from pydantic import TypeAdapter
    adapter = TypeAdapter(type)
    return adapter.validate_python(data)


def run_file(file_):
    import subprocess
    subprocess.call(['pytest', '--tb=short', str(file_)])