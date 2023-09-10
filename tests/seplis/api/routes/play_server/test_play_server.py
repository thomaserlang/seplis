import pytest
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas


@pytest.mark.asyncio
async def test_play_server(client: AsyncClient):
    await user_signin(client)
    r = await client.post('/2/play-servers', json={
        'name': 'Thomas',
        'url': 'http://example.net',
        'secret': 'a'*20,
    })
    assert r.status_code == 201, r.content
    server = schemas.Play_server_with_url.model_validate(r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example.net'    


    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 200, r.content
    server = schemas.Play_server_with_url.model_validate(r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example.net'

    r = await client.put(f'/2/play-servers/{server.id}', json={
        'url': 'http://example2.net',
        'secret': '2'*20,
    })
    assert r.status_code == 200, r.content
    server = schemas.Play_server_with_url.model_validate(r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example2.net'


    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 200, r.content
    server = schemas.Play_server_with_url.model_validate(r.json())
    
    r = await client.delete(f'/2/play-servers/{server.id}')
    assert r.status_code == 204, r.content
    

    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 404, r.content


if __name__ == '__main__':
    run_file(__file__)