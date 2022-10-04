from fastapi import APIRouter, Security, Depends
from starlette.concurrency import run_in_threadpool
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions
from passlib.hash import pbkdf2_sha256

router = APIRouter(prefix='/1')

@router.post('/token', status_code=201, response_model=schemas.Token)
async def create_token(
    data: schemas.Token_create,
    session: AsyncSession = Depends(get_session),
):
    app: models.App = await session.scalar(sa.select(models.App).where(models.App.client_id == data.client_id))
    if not app:
        raise exceptions.OAuth_unknown_client_id_exception(data.client_id)
    
    if app.level != constants.LEVEL_GOD:
        raise exceptions.OAuth_unauthorized_grant_type_level_request_exception(
            constants.LEVEL_GOD, app.level
        )
    
    user: models.User = await session.scalar(sa.select(models.User).where(sa.or_(
        models.User.email == data.email, 
        models.User.username == data.email,
    )))

    if not user:
        raise exceptions.Wrong_email_or_password_exception()

    matches = await run_in_threadpool(pbkdf2_sha256.verify, data.password, user.password if user else '')
    if not matches:
        raise exceptions.Wrong_email_or_password_exception()

    token = models.Token(
        app_id=app.id,
        user_id=user.id,
        user_level=user.level,
    )
    await session.commit()
    await token.cache()
    return schemas.Token(access_token=token.token)