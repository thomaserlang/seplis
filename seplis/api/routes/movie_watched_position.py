from fastapi import Depends, Security, APIRouter, Body, Response
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants


router = APIRouter(prefix='/2/movies/{movie_id}/watched-position')


@router.get('', response_model=schemas.Movie_watched)
async def get_position(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    ew = await session.scalar(sa.select(models.Movie_watched).where(
        models.Movie_watched.movie_id == movie_id,
        models.Movie_watched.user_id == user.id,
    ))
    if not ew:        
        return Response(status_code=204)
    return schemas.Movie_watched.model_validate(ew)
    

@router.put('', status_code=204)
async def set_position(
    movie_id: int, 
    position: int = Body(..., embed=True, ge=0, le=86400),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    await models.Movie_watched.set_position(
        user_id=user.id,
        movie_id=movie_id,
        position=position,
    )


@router.delete('', status_code=204)
async def delete_position(
    movie_id: int, 
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    await models.Movie_watched.reset_position(
        user_id=user.id,
        movie_id=movie_id,
    )