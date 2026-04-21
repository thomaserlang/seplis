from typing import Any

from httpx import AsyncClient

from seplis.api.user.actions.token_actions import create_token
from seplis.api.user.actions.user_actions import create_user


async def user_signin(client: AsyncClient, scopes: list[str] | None = None) -> int:
    if scopes is None:
        scopes = ['me']
    user = await create_user(
        data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '1' * 10,
        }
    )
    token = await create_token(user_id=user.id, expires_days=1, scopes=scopes)
    client.headers['Authorization'] = f'Bearer {token}'
    return user.id


def parse_obj_as(type: Any, data: Any) -> Any:
    from pydantic import TypeAdapter

    adapter = TypeAdapter(type)
    return adapter.validate_python(data)


def run_file(file_: Any) -> None:
    import subprocess

    subprocess.call(['pytest', '--tb=short', str(file_)])
