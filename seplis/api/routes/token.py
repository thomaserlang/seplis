from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Request, Security
from passlib.hash import pbkdf2_sha256
from starlette.concurrency import run_in_threadpool

from seplis.api.user import Token, TokenCreate, UserAuthenticated

from .. import exceptions
from ..dependencies import AsyncSession, authenticated, get_session
from ..user.actions.token_actions import create_token
from ..user.models.user_model import MUser

router = APIRouter(prefix='/2', tags=['Login'])


@router.post('/token', status_code=201)
async def create_token_route(
    data: TokenCreate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:

    user = await session.scalar(
        sa.select(MUser).where(
            sa.or_(
                MUser.email == data.login,
                MUser.username == data.login,
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

    token = await create_token(user_id=user.id, scopes=user.scopes)

    return Token(access_token=token)


@router.post('/progress-token', status_code=201)
async def create_progress_token_route(
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> Token:
    token = await create_token(user_id=user.id, scopes=['user:progress'], expires_days=1)
    return Token(access_token=token)
