import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models

@pytest.mark.asyncio
async def test_play_server(client: AsyncClient):
    await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    server = schemas.Play_server_with_url.parse_obj(r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example.net'    


    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 200, r.content
    server = schemas.Play_server_with_url.parse_obj(r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example.net'

    r = await client.put(f'/2/play-servers/{server.id}', json={
        'url': 'http://example2.net',
        'secret': '2'*20,
    })
    assert r.status_code == 200, r.content
    server = schemas.Play_server_with_url.parse_obj(r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example2.net'


    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 200, r.content
    server = schemas.Play_server_with_url.parse_obj(r.json())
    
    r = await client.delete(f'/2/play-servers/{server.id}')
    assert r.status_code == 204, r.content
    

    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 404, r.content


@pytest.mark.asyncio
async def test_play_server_invite(client: AsyncClient):
    user_id = await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    server = schemas.Play_server_with_url.parse_obj(r.json())

    r = await client.post(f'/2/play-servers/{server.id}/invites', json={
        'user_id': user_id,
    })
    assert r.status_code == 400, r.content
    data = schemas.Error.parse_obj(r.json())
    assert data.code == 2251, data.code


    user = await models.User.save(user_data=schemas.User_create(email='test2@example.com', username='test2', password='1'*10), user_id=None)
    
    r = await client.post(f'/2/play-servers/{server.id}/invites', json={
        'user_id': user.id,
    })
    assert r.status_code == 201, r.content
    data = schemas.Play_server_invite_id.parse_obj(r.json())
    assert data.invite_id != None


    r = await client.get(f'/2/play-servers/{server.id}/invites')
    assert r.status_code == 200, r.content
    invites = schemas.Page_result[schemas.Play_server_invite].parse_obj(r.json())
    assert invites.items[0].user.id == user.id
    assert invites.items[0].created_at != None
    assert invites.items[0].expires_at != None
    

    token = await models.Token.new_token(user_id=user.id)

    r = await client.post('/2/users/me/play-server-accept-invite', json={
        'invite_id': data.invite_id,
    })
    assert r.status_code == 400, r.content


    r = await client.post('/2/users/me/play-server-accept-invite', json={
        'invite_id': data.invite_id,
    }, headers={
        'Authorization': f'Bearer {token}',
    })
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/play-servers/{server.id}/invites')
    assert r.status_code == 200, r.content
    invites = schemas.Page_result[schemas.Play_server_invite].parse_obj(r.json())
    assert invites.total == 0


    r = await client.get(f'/2/play-servers/{server.id}/access')
    assert r.status_code == 200, r.content
    users = schemas.Page_result[schemas.Play_server_access].parse_obj(r.json())
    assert users.items[0].user.id == user.id
    assert users.items[1].user.id == user_id


if __name__ == '__main__':
    run_file(__file__)