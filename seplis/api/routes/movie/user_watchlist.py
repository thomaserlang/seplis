import sqlalchemy as sa
from fastapi import Depends, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
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
    w = await session.scalar(sa.select(models.MMovieWatchlist.created_at).where(
        models.MMovieWatchlist.user_id == user.id,
        models.MMovieWatchlist.movie_id == movie_id,
    ))
    if not w:
        return schemas.Movie_watchlist()
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
) -> None:
    await models.MMovieWatchlist.add(user_id=user.id, movie_id=movie_id)


@router.delete('/{movie_id}/watchlist', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def remove_from_watchlist(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),    
) -> None:
    await models.MMovieWatchlist.remove(user_id=user.id, movie_id=movie_id)