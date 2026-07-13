from fastapi import APIRouter

from ..actions.user_actions import create_user, get_users_by_username
from ..schemas.user_schemas import User, UserCreate, UserPublic

router = APIRouter(prefix='/users')


@router.post('', status_code=201)
async def create_user_route(user_data: UserCreate) -> User:
    return await create_user(user_data)


@router.get('')
async def get_users_route(username: str) -> list[UserPublic]:
    return await get_users_by_username(username=username)
