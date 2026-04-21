from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api import user
from seplis.api.dependencies import authenticated
from seplis.api.exceptions import Forbidden
from seplis.api.user.actions.token_actions import create_token

from ..actions.auth_code_actions import create_auth_code, redeem_auth_code
from ..schemas.auth_code_schemas import AuthCode, AuthCodeRedeem

router = APIRouter(prefix='/2', tags=['Login'])


@router.post('/auth-code', status_code=201)
async def create_auth_code_route(
    user_data: Annotated[user.UserAuthenticated, Security(authenticated, scopes=['me'])],
) -> AuthCode:
    return await create_auth_code(action_by_user_id=user_data.id, scopes=['me'])


@router.post('/auth-code/redeem', status_code=201)
async def redeem_auth_code_route(data: AuthCodeRedeem) -> user.Token:
    redeemed = await redeem_auth_code(data['code'])
    if not redeemed:
        raise Forbidden('Invalid auth code')

    token = await create_token(user_id=redeemed.user_id, scopes=redeemed.scopes)

    return user.Token(access_token=token)
