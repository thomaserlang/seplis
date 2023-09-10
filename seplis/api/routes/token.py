from fastapi import APIRouter, Depends, Security, Request
from starlette.concurrency import run_in_threadpool
from passlib.hash import pbkdf2_sha256
import sqlalchemy as sa

from seplis.api.send_email import send_new_login

from ..dependencies import get_session, AsyncSession, authenticated
from .. import models, schemas, constants, exceptions

router = APIRouter(prefix='/2', tags=['Login'])


@router.post('/token', status_code=201, response_model=schemas.Token)
async def create_token(
    data: schemas.Token_create,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    app: models.App = await session.scalar(sa.select(models.App).where(models.App.client_id == data.client_id))
    if not app:
        raise exceptions.OAuth_unknown_client_id_exception()
    
    if app.level != constants.LEVEL_GOD:
        raise exceptions.OAuth_unauthorized_grant_type_level_request_exception(
            constants.LEVEL_GOD, app.level
        )
    
    user: models.User = await session.scalar(sa.select(models.User).where(sa.or_(
        models.User.email == data.login, 
        models.User.username == data.login,
    )))

    if not user:
        raise exceptions.Wrong_login_or_password()

    try:
        matches = await run_in_threadpool(pbkdf2_sha256.verify, data.password, user.password if user else '')
    except:
        matches = False
    if not matches:
        raise exceptions.Wrong_login_or_password()
    
    token = await models.Token.new_token(user_id=user.id, app_id=app.id, scopes=user.scopes)
    
    await send_new_login(to=user.email, ip=request.client.host)
    
    return schemas.Token(access_token=token)


@router.post('/progress-token', status_code=201, response_model=schemas.Token)
async def create_progress_token(
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    token = await models.Token.new_token(user_id=user.id, scopes=['user:progress'], expires_days=1)
    return schemas.Token(access_token=token)