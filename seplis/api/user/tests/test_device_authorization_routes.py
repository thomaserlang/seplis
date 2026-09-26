from datetime import timedelta

import pytest

from seplis import config
from seplis.api import exceptions
from seplis.api.testbase import AsyncClient, run_file, user_signin
from seplis.api.user.actions.device_authorization_actions import (
    create_device_code,
    poll_device_authorization,
)
from seplis.utils import datetime_now


@pytest.fixture(autouse=True)
def device_authorization_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        config.web,
        'cookie_secret',
        'test-device-authorization-secret-value',
    )


@pytest.mark.asyncio
async def test_device_authorization(client: AsyncClient) -> None:
    response = await client.post('/2/device-authorization')
    assert response.status_code == 201, response.content
    authorization = response.json()
    assert len(authorization['user_code']) == 6
    assert authorization['user_code'].isdigit()
    assert len(authorization['device_code']) >= 32
    assert authorization['verification_uri'].endswith('/device')
    assert authorization['verification_uri_complete'].endswith(
        f'/device?code={authorization["user_code"]}'
    )
    assert authorization['poll_interval_seconds'] > 0

    response = await client.post(
        '/2/device-authorization/token',
        json={'device_code': authorization['device_code']},
    )
    assert response.status_code == 200, response.content
    assert response.json() == {
        'status': 'pending',
        'access_token': None,
        'token_type': None,
    }

    response = await client.post(
        '/2/device-authorization/approve',
        json={'user_code': authorization['user_code']},
    )
    assert response.status_code == 401, response.content

    user_id = await user_signin(client)
    response = await client.post(
        '/2/device-authorization/approve',
        json={
            'user_code': f'{authorization["user_code"][:3]}-'
            f'{authorization["user_code"][3:]}'
        },
    )
    assert response.status_code == 204, response.content

    response = await client.post(
        '/2/device-authorization/token',
        json={'device_code': authorization['device_code']},
    )
    assert response.status_code == 200, response.content
    token = response.json()
    assert token['status'] == 'authorized'
    assert token['token_type'] == 'bearer'
    assert token['access_token']

    client.headers['Authorization'] = f'Bearer {token["access_token"]}'
    response = await client.get('/2/users/me')
    assert response.status_code == 200, response.content
    assert response.json()['id'] == user_id

    response = await client.post(
        '/2/device-authorization/token',
        json={'device_code': authorization['device_code']},
    )
    assert response.status_code == 404, response.content


@pytest.mark.asyncio
async def test_device_authorization_rejects_unknown_codes(
    client: AsyncClient,
) -> None:
    await user_signin(client)
    response = await client.post(
        '/2/device-authorization/approve',
        json={'user_code': '999999'},
    )
    assert response.status_code == 404, response.content

    response = await client.post(
        '/2/device-authorization/token',
        json={'device_code': 'x' * 32},
    )
    assert response.status_code == 404, response.content


@pytest.mark.asyncio
async def test_device_authorization_rejects_invalid_jwt_before_database() -> None:
    with pytest.raises(exceptions.DeviceAuthorizationUnknown):
        await poll_device_authorization(device_code='x' * 32)


@pytest.mark.asyncio
async def test_device_authorization_rejects_forged_jwt_before_database() -> None:
    now = datetime_now()
    device_code = create_device_code(
        issued_at=now,
        expires_at=now + timedelta(minutes=10),
    )
    unsigned_token, _, _ = device_code.rpartition('.')
    forged_device_code = f'{unsigned_token}.{"x" * 43}'

    with pytest.raises(exceptions.DeviceAuthorizationUnknown):
        await poll_device_authorization(device_code=forged_device_code)


@pytest.mark.asyncio
async def test_device_authorization_rejects_expired_jwt_before_database() -> None:
    now = datetime_now()
    device_code = create_device_code(
        issued_at=now - timedelta(minutes=11),
        expires_at=now - timedelta(minutes=1),
    )

    with pytest.raises(exceptions.DeviceAuthorizationExpired):
        await poll_device_authorization(device_code=device_code)


if __name__ == '__main__':
    run_file(__file__)
