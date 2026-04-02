import sqlalchemy as sa
from fastapi import Depends

from ... import models, schemas
from ...dependencies import AsyncSession, get_session
from .router import router


@router.post('', response_model=schemas.User, status_code=201)
async def create_user(user_data: schemas.User_create) -> schemas.User_basic:
    return await models.MUser.save(user_data)


@router.get('', response_model=list[schemas.User_public])
async def get_users(
    username: str,
    session: AsyncSession = Depends(get_session),
):
    users = await session.scalars(sa.select(models.MUser).where(models.MUser.username == username))
    return [schemas.User_public.model_validate(u) for u in users]