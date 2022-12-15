from fastapi import APIRouter, Depends, Security
from starlette.concurrency import run_in_threadpool
from passlib.hash import pbkdf2_sha256
import sqlalchemy as sa
from datetime import datetime, timedelta

from ..dependencies import get_session, AsyncSession, authenticated
from .. import models, schemas, constants, exceptions

router = APIRouter(prefix='/2')


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
        models.User.email == data.username, 
        models.User.username == data.username,
    )))

    if not user:
        raise exceptions.Wrong_email_or_password_exception()

    matches = await run_in_threadpool(pbkdf2_sha256.verify, data.password, user.password if user else '')
    if not matches:
        raise exceptions.Wrong_email_or_password_exception()

    token = await models.Token.new_token(user_id=user.id, app_id=app.id, user_level=user.level)

    return schemas.Token(access_token=token)


@router.post('/progress-token', status_code=201, response_model=schemas.Token)
async def create_progress_token(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    token = await models.Token.new_token(user_id=user.id, user_level=constants.LEVEL_PROGRESS, expires_days=1)
    return schemas.Token(access_token=token)