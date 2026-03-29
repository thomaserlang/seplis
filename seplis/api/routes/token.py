from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Request, Security
from passlib.hash import pbkdf2_sha256
from starlette.concurrency import run_in_threadpool

from seplis.api.send_email import send_new_login

from .. import exceptions, models, schemas
from ..dependencies import AsyncSession, authenticated, get_session

router = APIRouter(prefix='/2', tags=['Login'])


@router.post('/token', status_code=201)
async def create_token_route(
    data: schemas.Token_create,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> schemas.Token:

    user = await session.scalar(
        sa.select(models.User).where(
            sa.or_(
                models.User.email == data.login,
                models.User.username == data.login,
            )
        )
    )

    if not user:
        raise exceptions.Wrong_login_or_password()

    try:
        matches = await run_in_threadpool(
            pbkdf2_sha256.verify, data.password, user.password if user else ''
        )
    except Exception:
        matches = False
    if not matches:
        raise exceptions.Wrong_login_or_password()

    token = await models.Token.new_token(user_id=user.id, scopes=user.scopes)

    await send_new_login(
        to=user.email, ip=request.client.host if request.client else 'unknown'
    )

    return schemas.Token(access_token=token)


@router.post('/progress-token', status_code=201)
async def create_progress_token_route(
    user: Annotated[
        schemas.User_authenticated, Security(authenticated, scopes=['user:progress'])
    ],
) -> schemas.Token:
    token = await models.Token.new_token(
        user_id=user.id, scopes=['user:progress'], expires_days=1
    )
    return schemas.Token(access_token=token)
