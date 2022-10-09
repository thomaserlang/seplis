import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api.database import database
from seplis.api import models, constants
from seplis import utils

@pytest.mark.asyncio
async def test_token(client: AsyncClient):
    r = await client.post('/2/users', json={
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


    # wrong client id
    r = await client.post('/2/token', json={
        'client_id': 'WRONG',
        'username': 'testuser1',
        'password': '1234567890',
        'grant_type': 'password',
    })
    assert r.status_code == 400, r.content
    error = utils.json_loads(r.content)
    assert error['code'] == 1007


    # wrong password
    r = await client.post('/2/token', json={
        'client_id': app.client_id,
        'username': 'testuser1',
        'password': 'WRONG',
        'grant_type': 'password',
    })
    assert r.status_code == 401, r.content
    error = utils.json_loads(r.content)
    assert error['code'] == 1000


    # wrong username
    r = await client.post('/2/token', json={
        'client_id': app.client_id,
        'username': 'WRONG',
        'password': '1234567890',
        'grant_type': 'password',
    })
    assert r.status_code == 401, r.content
    assert error['code'] == 1000


    # correct password
    r = await client.post('/2/token', json={
        'client_id': app.client_id,
        'username': 'testuser1',
        'password': '1234567890',
        'grant_type': 'password',
    })
    assert r.status_code == 201, r.content
    data = utils.json_loads(r.content)
    assert len(data['access_token']) > 1
    

    r = await client.post('/2/token', json={
        'client_id': app.client_id,
        'username': 'test1@example.net',
        'password': '1234567890',
        'grant_type': 'password',
    })
    assert r.status_code == 201, r.content
    data = utils.json_loads(r.content)
    assert len(data['access_token']) > 1
    

    client.headers['Authorization'] = f'Bearer {data["access_token"]}'
    r = await client.post('/2/progress-token')
    assert r.status_code == 201, r.content
    data = utils.json_loads(r.content)
    assert len(data['access_token']) > 1


if __name__ == '__main__':
    run_file(__file__)