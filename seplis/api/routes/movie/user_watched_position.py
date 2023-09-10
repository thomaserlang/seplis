from fastapi import Depends, Security, Body, Response
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router


@router.get('/{movie_id}/watched-position', response_model=schemas.Movie_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def get_position(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    ew = await session.scalar(sa.select(models.Movie_watched).where(
        models.Movie_watched.movie_id == movie_id,
        models.Movie_watched.user_id == user.id,
    ))
    if not ew:        
        return Response(status_code=204)
    return schemas.Movie_watched.model_validate(ew)
    

@router.put('/{movie_id}/watched-position', status_code=204,
            description='''
            **Scope required:** `user:progress`
            ''')
async def set_position(
    movie_id: int, 
    position: int = Body(..., embed=True, ge=0, le=86400),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    await models.Movie_watched.set_position(
        user_id=user.id,
        movie_id=movie_id,
        position=position,
    )


@router.delete('/{movie_id}/watched-position', status_code=204,
            description='''
            **Scope required:** `user:progress`
            ''')
async def delete_position(
    movie_id: int, 
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    await models.Movie_watched.reset_position(
        user_id=user.id,
        movie_id=movie_id,
    )