import pytest

from seplis.api.play_server import PlayServerWithUrl
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin


@pytest.mark.asyncio
async def test_play_server(client: AsyncClient) -> None:
    await user_signin(client)
    r = await client.post(
        '/2/play-servers',
        json={
            'name': 'Thomas',
            'url': 'http://example.net',
            'secret': 'a' * 32,
        },
    )
    assert r.status_code == 201, r.content
    server = parse_obj_as(PlayServerWithUrl, r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example.net'

    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 200, r.content
    server = parse_obj_as(PlayServerWithUrl, r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example.net'

    r = await client.put(
        f'/2/play-servers/{server.id}',
        json={
            'url': 'http://example2.net',
            'secret': '2' * 32,
        },
    )
    assert r.status_code == 200, r.content
    server = parse_obj_as(PlayServerWithUrl, r.json())
    assert server.name == 'Thomas'
    assert server.url == 'http://example2.net'

    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 200, r.content
    server = parse_obj_as(PlayServerWithUrl, r.json())

    r = await client.delete(f'/2/play-servers/{server.id}')
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/play-servers/{server.id}')
    assert r.status_code == 404, r.content


if __name__ == '__main__':
    run_file(__file__)
