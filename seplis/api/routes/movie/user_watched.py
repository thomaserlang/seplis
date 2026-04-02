import sqlalchemy as sa
from fastapi import Depends, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get('/{movie_id}/watched', response_model=schemas.Movie_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def get_watched(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    w = await session.scalar(sa.select(models.MMovieWatched).where(
        models.MMovieWatched.user_id == user.id,
        models.MMovieWatched.movie_id == movie_id,
    ))
    return schemas.Movie_watched.model_validate(w) if w else schemas.Movie_watched()


@router.post('/{movie_id}/watched', response_model=schemas.Movie_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def watched_increment(
    movie_id: int,
    request: dict | None = None,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):  
    data = schemas.Movie_watched_increment.model_validate(request) if request else schemas.Movie_watched_increment()
    w = await models.MMovieWatched.increment(
        user_id=user.id,
        movie_id=movie_id,
        data=data,
    )
    return w if w else schemas.Movie_watched()


@router.delete('/{movie_id}/watched', response_model=schemas.Movie_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def watched_decrement(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),    
):
    w = await models.MMovieWatched.decrement(
        user_id=user.id,
        movie_id=movie_id,
    )
    return w if w else schemas.Movie_watched()