
import sqlalchemy as sa
from fastapi import Depends, Response, Body
from pydantic import EmailStr
from datetime import datetime, timezone
from ...dependencies import  get_session, AsyncSession
from ... import models, schemas, exceptions
from ...send_email import send_reset_password
from .router import router

@router.post('/send-reset-password', status_code=204)
async def send_reset_link(
    email: EmailStr = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    user_id = await session.scalar(sa.select(models.User.id).where(models.User.email == email))
    if not user_id:
        return Response(status_code=204)    
    url = await models.Reset_password.create_reset_link(user_id)
    await send_reset_password(to=email, url=url)


@router.post('/reset-password', status_code=204)
async def reset_password(
    key: str = Body(..., embed=True, min_length=36),
    new_password: schemas.USER_PASSWORD_TYPE = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    user_id = await session.scalar(sa.select(models.Reset_password.user_id).where(
        models.Reset_password.key == key,
        models.Reset_password.expires >= datetime.now(tz=timezone.utc),
    ))
    if not user_id:
        raise exceptions.Forbidden('Invalid reset key')
    
    await models.User.change_password(user_id=user_id, new_password=new_password)