
import sqlalchemy as sa
import aiosmtplib
from fastapi import APIRouter, Depends, Response, Body
from pydantic import EmailStr
from datetime import datetime, timezone
from email.mime.text import MIMEText
from ..dependencies import  get_session, AsyncSession
from .. import models, schemas, exceptions
from ... import config, logger

router = APIRouter(prefix='/2')

@router.post('/send-reset-password', status_code=204)
async def send_reset_link(
    response: Response,
    email: EmailStr = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    user_id = await session.scalar(sa.select(models.User.id).where(models.User.email == email))
    if not user_id:
        response.status_code = 204
        return
    
    url = await models.Reset_password.create_reset_url(user_id)

    smtp = aiosmtplib.SMTP(
        hostname=config.data.smtp.server, 
        port=int(config.data.smtp.port),
        use_tls=config.data.smtp.use_tls,
    )
    await smtp.connect()
    if config.data.smtp.user:
        await smtp.login(config.data.smtp.user, config.data.smtp.password)

    message = MIMEText(f'''
    <html>
    <body>
        Reset your SEPLIS password here: <a href="{url}">{url}</a>
    </body>
    </html>
    ''', 'html')
    message["From"] = config.data.smtp.from_email
    message["To"] = email
    message["Subject"] = "SEPLIS Reset password"
    await smtp.send_message(message)


@router.post('/reset-password', status_code=204)
async def reset_password(
    key = Body(..., embed=True, min_length=36),
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