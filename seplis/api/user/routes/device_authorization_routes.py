from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.dependencies import authenticated

from ..actions.device_authorization_actions import (
    approve_device_authorization,
    create_device_authorization,
    poll_device_authorization,
)
from ..schemas.device_authorization_schemas import (
    DeviceAuthorization,
    DeviceAuthorizationApprove,
    DeviceAuthorizationToken,
    DeviceAuthorizationTokenRequest,
)
from ..schemas.user_authentication_schemas import UserAuthenticated

router = APIRouter(prefix='/device-authorization', tags=['Login'])


@router.post('', status_code=201)
async def create_device_authorization_route() -> DeviceAuthorization:
    return await create_device_authorization()


@router.post('/approve', status_code=204)
async def approve_device_authorization_route(
    data: DeviceAuthorizationApprove,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['me'])],
) -> None:
    await approve_device_authorization(user_code=data['user_code'], user_id=user.id)


@router.post('/token')
async def poll_device_authorization_route(
    data: DeviceAuthorizationTokenRequest,
) -> DeviceAuthorizationToken:
    return await poll_device_authorization(device_code=data['device_code'])
