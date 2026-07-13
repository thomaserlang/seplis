import pytest

from seplis.api.common import Error
from seplis.api.page_cursor import PageCursor
from seplis.api.play_server import (
    PlayServerAccess,
    PlayServerInvite,
    PlayServerInviteId,
    PlayServerWithUrl,
)
from seplis.api.testbase import AsyncClient, parse_obj_as, run_file, user_signin
from seplis.api.user import create_token, create_user


@pytest.mark.asyncio
async def test_play_server_invite(client: AsyncClient) -> None:
    user_id = await user_signin(client)
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

    r = await client.post(
        f'/2/play-servers/{server.id}/invites',
        json={
            'user_id': user_id,
        },
    )
    assert r.status_code == 400, r.content
    data = parse_obj_as(Error, r.json())
    assert data.code == 2251, data.code

    user = await create_user(
        data={
            'email': 'test2@example.com',
            'username': 'test2',
            'password': '1' * 10,
        }
    )

    r = await client.post(
        f'/2/play-servers/{server.id}/invites',
        json={
            'user_id': user.id,
        },
    )
    assert r.status_code == 201, r.content
    data = parse_obj_as(PlayServerInviteId, r.json())
    assert data.invite_id is not None

    r = await client.get(f'/2/play-servers/{server.id}/invites')
    assert r.status_code == 200, r.content
    invites = parse_obj_as(PageCursor[PlayServerInvite], r.json())
    assert invites.records[0].user.id == user.id
    assert invites.records[0].created_at is not None
    assert invites.records[0].expires_at is not None

    token = await create_token(user_id=user.id, scopes=['me'])

    r = await client.post(
        '/2/play-servers/accept-invite',
        json={
            'invite_id': data.invite_id,
        },
    )
    assert r.status_code == 400, r.content

    r = await client.post(
        '/2/play-servers/accept-invite',
        json={
            'invite_id': data.invite_id,
        },
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert r.status_code == 204, r.content

    r = await client.get(f'/2/play-servers/{server.id}/invites')
    assert r.status_code == 200, r.content
    invites = parse_obj_as(PageCursor[PlayServerInvite], r.json())
    assert invites.total == 0

    r = await client.get(f'/2/play-servers/{server.id}/access')
    assert r.status_code == 200, r.content
    users = parse_obj_as(PageCursor[PlayServerAccess], r.json())
    assert users.records[0].user.id == user.id
    assert users.records[1].user.id == user_id


if __name__ == '__main__':
    run_file(__file__)
