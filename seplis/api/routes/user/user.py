import sqlalchemy as sa
from fastapi import Depends

from seplis.api.user import MUser, User, UserBasic, UserCreate, UserPublic, create_user

from ...dependencies import AsyncSession, get_session
from .router import router


@router.post('', response_model=User, status_code=201)
async def create_user_route(user_data: UserCreate) -> UserBasic:
    return await create_user(user_data)


@router.get('', response_model=list[UserPublic])
async def get_users(
    username: str,
    session: AsyncSession = Depends(get_session),
) -> list[UserPublic]:
    users = await session.scalars(sa.select(MUser).where(MUser.username == username))
    return [UserPublic.model_validate(u) for u in users]
