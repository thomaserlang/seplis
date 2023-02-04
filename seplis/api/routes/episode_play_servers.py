from fastapi import APIRouter, Depends, Security
import sqlalchemy as sa
from tornado import web
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants

router = APIRouter(prefix='/2/series/{series_id}/episodes/{episode_number}/play-servers')

@router.get('', response_model=list[schemas.Play_request])
async def get_episode_play_servers(
    series_id: int, 
    episode_number: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    query: list[models.Play_server] = await session.scalars(sa.select(models.Play_server).where(
        models.Play_server_access.user_id == user.id,
        models.Play_server.id == models.Play_server_access.play_server_id,
        models.Play_server_episode.play_server_id == models.Play_server.id,
        models.Play_server_episode.series_id == series_id,
        models.Play_server_episode.episode_number == episode_number,
    ))
    play_ids: list[schemas.Play_request] = []
    for row in query:
        play_ids.append(schemas.Play_request(
            play_id=web.create_signed_value(
                secret=row.secret,
                name='play_id',
                value=schemas.Play_id_info_episode(
                    series_id=series_id,
                    number=episode_number,
                ).json(),
                version=2,
            ).decode('utf-8'),
            play_url=row.url,
        ))
    return play_ids