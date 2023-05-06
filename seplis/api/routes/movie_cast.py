import sqlalchemy as sa
from fastapi import APIRouter, Depends, Security
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/movies/{movie_id}/cast')

@router.put('', status_code=204)
async def movie_cast_add(
    movie_id: int,
    data: schemas.Movie_cast_person_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    data.movie_id = movie_id
    await models.Movie_cast.save(data=data)


@router.delete('', status_code=204)
async def movie_cast_delete(
    movie_id: int,
    person_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    await models.Movie_cast.delete(
        movie_id=movie_id,
        person_id=person_id,
    )


@router.get('', response_model=schemas.Page_cursor_result[schemas.Movie_cast_person])
async def movie_cast_get(
    movie_id: int,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Movie_cast).where(
        models.Movie_cast.movie_id == movie_id,
    ).order_by(
        sa.desc(models.Movie_cast.order),
    )
    p = await utils.sqlalchemy.paginate_cursor(
        session=session,
        query=query,
        page_query=page_query,
    )
    p.items = [schemas.Movie_cast_person.from_orm(row[0]) for row in p.items]
    return p