from fastapi import Depends, Security, APIRouter
import sqlalchemy as sa
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants


router = APIRouter(prefix='/2/movies/{movie_id}/watchlist')


@router.get('', response_model=schemas.Movie_watchlist)
async def get_watchlist(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
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


@router.put('', status_code=204)
async def add_to_watchlist(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    await models.Movie_watchlist.add(user_id=user.id, movie_id=movie_id)


@router.delete('', status_code=204)
async def remove_from_watchlist(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),    
):
    await models.Movie_watchlist.remove(user_id=user.id, movie_id=movie_id)