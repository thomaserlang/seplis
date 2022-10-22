from fastapi import Depends, Security, Response, APIRouter
import sqlalchemy as sa
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants

router = APIRouter(prefix='/2/movies/{movie_id}/watched')

@router.get('', response_model=schemas.Movie_watched)
async def get_watched(
    movie_id: int,
    response: Response,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    w = await session.scalar(sa.select(models.Movie_watched).where(
        models.Movie_watched.user_id == user.id,
        models.Movie_watched.movie_id == movie_id,
    ))
    if not w:
        response.status_code = 204
    else:
        return schemas.Movie_watched.from_orm(w)


@router.post('', response_model=schemas.Movie_watched)
async def watched_increment(
    movie_id: int,
    response: Response,
    request: dict | None = None,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):  
    data = schemas.Movie_watched_increment.parse_obj(request) if request else schemas.Movie_watched_increment()
    w = await models.Movie_watched.increment(
        user_id=user.id,
        movie_id=movie_id,
        data=data,
    )
    if w:
        return w
    else:
        response.status_code = 204


@router.delete('', response_model=schemas.Movie_watched)
async def watched_decrement(
    movie_id: int,
    response: Response,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),    
):
    w = await models.Movie_watched.decrement(
        user_id=user.id,
        movie_id=movie_id,
    )
    if w:
        return w
    else:
        response.status_code = 204