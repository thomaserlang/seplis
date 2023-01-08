import pytest_asyncio
from httpx import AsyncClient
from seplis import config, config_load
from seplis.api import  constants, models
from seplis.api.main import app
from seplis.api import schemas
from seplis import logger


@pytest_asyncio.fixture(scope='function')
async def client():
    from seplis.api.database import database
    config_load()
    config.data.test = True
    await database.setup_test()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    await database.close_test()


async def user_signin(client: AsyncClient, scopes: list[str] = [str(constants.LEVEL_USER)], app_level=constants.LEVEL_GOD) -> int:
    user = await models.User.save(user_data=schemas.User_create(
        username='testuser',
        email='test@example.com',
        level=int(scopes[0]),
        password='1'*10,
    ))
    token = await models.Token.new_token(user_id=user.id, expires_days=1, user_level=int(scopes[0]))
    client.headers['Authorization'] = f'Bearer {token}'
    return user.id


def run_file(file_):
    import subprocess
    subprocess.call(['pytest', '--tb=short', str(file_)])