import sqlalchemy as sa
from fastapi import Depends, Security

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.put('/{movie_id}/cast', status_code=204,
            description='''
            **Scope required:** `movie:edit`
            ''')
async def movie_cast_add(
    movie_id: int,
    data: schemas.Movie_cast_person_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=['movie:edit']),
) -> None:
    data.movie_id = movie_id
    await models.MMovieCast.save(data=data)


@router.delete('/{movie_id}/cast', status_code=204)
async def movie_cast_delete(
    movie_id: int,
    person_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['movie:edit']),
) -> None:
    await models.MMovieCast.delete(
        movie_id=movie_id,
        person_id=person_id,
    )


@router.get('/{movie_id}/cast', response_model=schemas.Page_cursor_result[schemas.Movie_cast_person])
async def movie_cast_get(
    movie_id: int,
    page_query: schemas.Page_cursor_query = Depends(),
    order_le: int = None,
    order_ge: int = None,
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.MMovieCast).where(
        models.MMovieCast.movie_id == movie_id,
    ).order_by(
        sa.asc(models.MMovieCast.order),
    )
    
    if order_le is not None:
        query = query.where(models.MMovieCast.order <= order_le)
    if order_ge is not None:
        query = query.where(models.MMovieCast.order >= order_ge)

    p = await utils.sqlalchemy.paginate_cursor(
        session=session,
        query=query,
        page_query=page_query,
    )
    p.items = [schemas.Movie_cast_person.model_validate(row[0]) for row in p.items]
    return p