from typing import Annotated

from fastapi import APIRouter, Body
from pydantic import EmailStr

from seplis.api.user import PasswordStr, change_password

from ..actions.reset_password_actions import get_reset_password_user_id, send_reset_link

router = APIRouter()


@router.post('/send-reset-password', status_code=204)
async def send_reset_link_route(
    email: Annotated[EmailStr, Body(..., embed=True)],
) -> None:
    await send_reset_link(email=str(email))


@router.post('/reset-password', status_code=204)
async def reset_password_route(
    key: Annotated[str, Body(..., embed=True, min_length=36)],
    new_password: Annotated[PasswordStr, Body(..., embed=True)],
) -> None:
    user_id = await get_reset_password_user_id(key=key)
    await change_password(user_id=user_id, new_password=new_password)
