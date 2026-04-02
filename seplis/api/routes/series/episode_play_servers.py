import jwt
import sqlalchemy as sa
from fastapi import Depends, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get('/{series_id}/episodes/{episode_number}/play-servers', response_model=list[schemas.Play_request],
            description='''
            **Scope required:** `user:play`
            ''')
async def get_episode_play_servers(
    series_id: int, 
    episode_number: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:play']),
):
    query: list[models.MPlayServer] = await session.scalars(sa.select(models.MPlayServer).where(
        models.MPlayServerAccess.user_id == user.id,
        models.MPlayServer.id == models.MPlayServerAccess.play_server_id,
        models.MPlayServerEpisode.play_server_id == models.MPlayServer.id,
        models.MPlayServerEpisode.series_id == series_id,
        models.MPlayServerEpisode.episode_number == episode_number,
    ))
    play_ids: list[schemas.Play_request] = []
    for row in query:
        play_ids.append(schemas.Play_request(
            play_id=jwt.encode(
                schemas.Play_id_info_episode(
                    series_id=series_id,
                    number=episode_number,
                ).model_dump(),
                row.secret,
                algorithm="HS256",
            ),
            play_url=row.url,
        ))
    return play_ids