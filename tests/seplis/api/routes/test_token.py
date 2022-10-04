import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api.database import database
from seplis.api import models, constants

@pytest.mark.asyncio
async def test_token(client: AsyncClient):
    r = await client.post('/1/users', json={
        'username': 'testuser1',
        'email': 'test1@example.net',
        'password': '1234567890',
    })
    async with database.session() as session:
        app = models.App(
            user_id=1,
            name='testbase app',
            redirect_uri='',
            level=constants.LEVEL_GOD,
        )
        session.add(app)
        await session.commit()

    r = await client.post('/1/token', json={
        'client_id': app.client_id,
        'email': 'testuser1',
        'password': '1234567890',
        'grant_type': 'password',
    })
    assert r.status_code == 201, r.content

if __name__ == '__main__':
    run_file(__file__)