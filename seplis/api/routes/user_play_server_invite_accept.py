from fastapi import APIRouter, Security

from ..dependencies import authenticated
from .. import models, schemas, constants


router = APIRouter(prefix='/2/users/me/play-server-accept-invite')


@router.post('', status_code=204)
async def accept_play_server_invite(
    data: schemas.Play_server_invite_id,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_servers']),
):
    await models.Play_server_invite.accept_invite(
        user_id=user.id,
        invite_id=data.invite_id,
    )