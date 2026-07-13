from typing import Annotated

from fastapi import APIRouter, Request, Security

from ...dependencies import authenticated
from ..actions.token_actions import create_login_token, create_progress_token
from ..schemas.user_authentication_schemas import Token, TokenCreate, UserAuthenticated

router = APIRouter(tags=['Login'])


@router.post('/token', status_code=201)
async def create_token_route(
    data: TokenCreate,
    request: Request,
) -> Token:
    return await create_login_token(data=data)


@router.post('/progress-token', status_code=201)
async def create_progress_token_route(
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> Token:
    return await create_progress_token(user.id)
