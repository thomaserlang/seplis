from fastapi import APIRouter, Depends, Request, Security

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/movies-stared')

@router.get('', response_model=schemas.Page_result[schemas.Movie_user])
async def get_movies_stared(
    request: Request,
    sort: schemas.MOVIE_USER_SORT_TYPE = 'stared_desc',
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = models.movie_user_query(user_id=user.id, sort=sort).where(
        models.Movie_stared.user_id == user.id,
        models.Movie.id == models.Movie_stared.movie_id,
    )

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request, scalars=False)
    p.items = [models.movie_user_result_parse(item) for item in p.items]
    return p