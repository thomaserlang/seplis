from datetime import UTC, datetime

import sqlalchemy as sa
from fastapi import Body, Depends, Response
from pydantic import EmailStr

from ... import exceptions, models, schemas
from ...dependencies import AsyncSession, get_session
from ...send_email import send_reset_password
from .router import router


@router.post('/send-reset-password', status_code=204)
async def send_reset_link(
    email: EmailStr = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    user_id = await session.scalar(
        sa.select(models.User.id).where(models.User.email == email)
    )
    if not user_id:
        return Response(status_code=204)
    url = await models.Reset_password.create_reset_link(user_id)
    await send_reset_password(to=email, url=url)


@router.post('/reset-password', status_code=204)
async def reset_password(
    key: str = Body(..., embed=True, min_length=36),
    new_password: schemas.PasswordStr = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    user_id = await session.scalar(
        sa.select(models.Reset_password.user_id).where(
            models.Reset_password.key == key,
            models.Reset_password.expires >= datetime.now(tz=UTC),
        )
    )
    if not user_id:
        raise exceptions.Forbidden('Invalid reset key')

    await models.User.change_password(user_id=user_id, new_password=new_password)
