from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router


@router.get('/{movie_id}/watchlist', response_model=schemas.Movie_watchlist,
            description='''
            **Scope required:** `user:view_lists`
            ''')
async def get_watchlist(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
):
    w = await session.scalar(sa.select(models.Movie_watchlist.created_at).where(
        models.Movie_watchlist.user_id == user.id,
        models.Movie_watchlist.movie_id == movie_id,
    ))
    if not w:
        return schemas.Movie_watchlist()
    else:
        return schemas.Movie_watchlist(
            on_watchlist=True,
            created_at=w,
        )


@router.put('/{movie_id}/watchlist', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def add_to_watchlist(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Movie_watchlist.add(user_id=user.id, movie_id=movie_id)


@router.delete('/{movie_id}/watchlist', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def remove_from_watchlist(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),    
):
    await models.Movie_watchlist.remove(user_id=user.id, movie_id=movie_id)