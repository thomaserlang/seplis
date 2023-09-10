import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin

@pytest.mark.asyncio
async def test_user(client: AsyncClient):

    r = await client.post('/2/users', json={
        'username': 'testuser1',
        'email': 'test1@example.net',
        'password': '1234567890',
    })
    assert r.status_code == 201, r.content
    user = r.json()
    assert user['username'] == 'testuser1'
    assert user['email'] == 'test1@example.net'

    # Test duplicate
    r = await client.post('/2/users', json={
        'username': 'testuser1',
        'email': 'test2@example.net',
        'password': '1234567890',
    })
    assert r.status_code == 400, r.content
    error = r.json()
    assert error['code'] == 1502

    r = await client.post('/2/users', json={
        'username': 'testuser2',
        'email': 'test1@example.net',
        'password': '1234567890',
    })
    assert r.status_code == 400, r.content
    error = r.json()
    assert error['code'] == 1501

    r = await client.get('/2/users/me')
    assert r.status_code == 401, r.content
    
    await user_signin(client)
    r = await client.get('/2/users/me')
    assert r.status_code == 200, r.content
    user = r.json()
    assert user['username'] == 'testuser'

    r = await client.put('/2/users/me', json={
        'username': 'testuser2',
        'email': 'test2@example.net',
    })
    assert r.status_code == 200, r.content
    user = r.json()
    assert user['username'] == 'testuser2'
    assert user['email'] == 'test2@example.net'


    r = await client.post('/2/users/me/change-password', json={
        'current_password': '12345',
        'new_password': '1234567890',
    })
    assert r.status_code == 400, r.content

    r = await client.post('/2/users/me/change-password', json={
        'current_password': '1'*10,
        'new_password': '12345678901',
    })
    assert r.status_code == 204, r.content    
    
    # make sure our current token didn't expire
    r = await client.get('/2/users/me')
    assert r.status_code == 200, r.content
    user = r.json()
    assert user['username'] == 'testuser2'


    r = await client.get('/2/users?username=testuser2')
    assert r.status_code == 200, r.content
    data = r.json()
    assert data[0]['id'] == user['id']


if __name__ == '__main__':
    run_file(__file__)