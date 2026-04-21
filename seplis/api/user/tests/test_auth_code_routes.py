import pytest

from seplis.api import schemas
from seplis.api.testbase import AsyncClient, run_file, user_signin
from seplis.api.user import Token


@pytest.mark.asyncio
async def test_auth_code_create_and_redeem(client: AsyncClient) -> None:
    user_id = await user_signin(client)

    r = await client.post('/2/auth-code')
    assert r.status_code == 201, r.content
    auth_code = r.json()
    code = auth_code['code']
    assert len(code) == 6
    assert code.isdigit()
    assert auth_code.get('expires_at') is not None

    r = await client.post('/2/auth-code/redeem', json={'code': code})
    assert r.status_code == 201, r.content
    redeemed = Token.model_validate(r.json())
    assert len(redeemed.access_token) > 1

    r = await client.post('/2/auth-code/redeem', json={'code': code})
    assert r.status_code == 403, r.content
    error = schemas.Error.model_validate(r.json())
    assert error.code == 501

    client.headers['Authorization'] = f'Bearer {redeemed.access_token}'
    r = await client.get('/2/users/me')
    assert r.status_code == 200, r.content
    user_data = r.json()
    assert user_data['id'] == user_id


@pytest.mark.asyncio
async def test_auth_code_redeem_invalid(client: AsyncClient) -> None:
    r = await client.post('/2/auth-code/redeem', json={'code': '999999'})
    assert r.status_code == 403, r.content
    error = schemas.Error.model_validate(r.json())
    assert error.code == 501


if __name__ == '__main__':
    run_file(__file__)
