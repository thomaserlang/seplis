from fastapi import APIRouter, Depends, Security
import sqlalchemy as sa
import jwt
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants

router = APIRouter(prefix='/2/movies/{movie_id}/play-servers')

@router.get('', response_model=list[schemas.Play_request])
async def get_movie_play_servers(
    movie_id: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    query: list[models.Play_server] = await session.scalars(sa.select(models.Play_server).where(
        models.Play_server_access.user_id == user.id,
        models.Play_server.id == models.Play_server_access.play_server_id,
        models.Play_server_movie.play_server_id == models.Play_server.id,
        models.Play_server_movie.movie_id == movie_id,
    ))
    play_ids: list[schemas.Play_request] = []
    for row in query:
        play_ids.append(schemas.Play_request(
            play_id=jwt.encode(
                schemas.Play_id_info_movie(
                    movie_id=movie_id,
                ).model_dump(),
                row.secret,
                algorithm='HS256',
            ),
            play_url=row.url,
        ))
    return play_ids