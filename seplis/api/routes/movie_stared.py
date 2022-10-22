from fastapi import Depends, Security, APIRouter
import sqlalchemy as sa
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import logger

router = APIRouter(prefix='/2/movies/{movie_id}/stared')

@router.get('', response_model=schemas.Movie_stared)
async def get_stared(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    w = await session.scalar(sa.select(models.Movie_stared.created_at).where(
        models.Movie_stared.user_id == user.id,
        models.Movie_stared.movie_id == movie_id,
    ))
    if not w:
        return schemas.Movie_stared()
    else:
        return schemas.Movie_stared(
            stared=True,
            created_at=w,
        )


@router.put('', status_code=204)
async def set_stared(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    await models.Movie_stared.set_stared(user_id=user.id, movie_id=movie_id)


@router.delete('', status_code=204)
async def remove_stared(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),    
):
    await models.Movie_stared.remove_stared(user_id=user.id, movie_id=movie_id)