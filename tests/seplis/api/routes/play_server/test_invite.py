import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models


@pytest.mark.asyncio
async def test_play_server_invite(client: AsyncClient):
    user_id = await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    server = schemas.Play_server_with_url.model_validate(r.json())

    r = await client.post(f'/2/play-servers/{server.id}/invites', json={
        'user_id': user_id,
    })
    assert r.status_code == 400, r.content
    data = schemas.Error.model_validate(r.json())
    assert data.code == 2251, data.code


    user = await models.User.save(data=schemas.User_create(email='test2@example.com', username='test2', password='1'*10), user_id=None)
    
    r = await client.post(f'/2/play-servers/{server.id}/invites', json={
        'user_id': user.id,
    })
    assert r.status_code == 201, r.content
    data = schemas.Play_server_invite_id.model_validate(r.json())
    assert data.invite_id != None


    r = await client.get(f'/2/play-servers/{server.id}/invites')
    assert r.status_code == 200, r.content
    invites = schemas.Page_cursor_total_result[schemas.Play_server_invite].model_validate(r.json())
    assert invites.items[0].user.id == user.id
    assert invites.items[0].created_at != None
    assert invites.items[0].expires_at != None
    

    token = await models.Token.new_token(user_id=user.id, scopes=['me'])

    r = await client.post('/2/play-servers/accept-invite', json={
        'invite_id': data.invite_id,
    })
    assert r.status_code == 400, r.content


    r = await client.post('/2/play-servers/accept-invite', json={
        'invite_id': data.invite_id,
    }, headers={
        'Authorization': f'Bearer {token}',
    })
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/play-servers/{server.id}/invites')
    assert r.status_code == 200, r.content
    invites = schemas.Page_cursor_total_result[schemas.Play_server_invite].model_validate(r.json())
    assert invites.total == 0


    r = await client.get(f'/2/play-servers/{server.id}/access')
    assert r.status_code == 200, r.content
    users = schemas.Page_cursor_total_result[schemas.Play_server_access].model_validate(r.json())
    assert users.items[0].user.id == user.id
    assert users.items[1].user.id == user_id


if __name__ == '__main__':
    run_file(__file__)