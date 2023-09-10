from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router


@router.get('/{movie_id}/favorite', response_model=schemas.Movie_favorite,
            description='''
            **Scope required:** `user:view_lists`
            ''')
async def get_favorite(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
):
    w = await session.scalar(sa.select(models.Movie_favorite.created_at).where(
        models.Movie_favorite.user_id == user.id,
        models.Movie_favorite.movie_id == movie_id,
    ))
    if not w:
        return schemas.Movie_favorite()
    else:
        return schemas.Movie_favorite(
            favorite=True,
            created_at=w,
        )


@router.put('/{movie_id}/favorite', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def add_to_favorite(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Movie_favorite.add(user_id=user.id, movie_id=movie_id)


@router.delete('/{movie_id}/favorite', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def remove_from_favorite(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),    
):
    await models.Movie_favorite.remove(user_id=user.id, movie_id=movie_id)