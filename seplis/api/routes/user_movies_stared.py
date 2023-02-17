from fastapi import APIRouter, Depends, Security

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/movies-stared')

@router.get('', response_model=schemas.Page_cursor_total_result[schemas.Movie_user])
async def get_movies_stared(
    sort: schemas.MOVIE_USER_SORT_TYPE = 'stared_at_desc',
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
    filter_query: schemas.Movie_user_query_filter = Depends(),
):
    query = models.movie_user_query(user_id=user.id, sort=sort, filter_query=filter_query).where(
        models.Movie_stared.user_id == user.id,
        models.Movie.id == models.Movie_stared.movie_id,
    )

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [models.movie_user_result_parse(item) for item in p.items]
    return p