import sqlalchemy as sa
from fastapi import APIRouter, Depends, Security
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/series/{series_id}/cast')


@router.put('', status_code=204)
async def series_cast_add(
    series_id: int,
    cast_member: schemas.Series_cast_person_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    cast_member.series_id = series_id
    await models.Series_cast.save(data=cast_member)


@router.delete('', status_code=204)
async def series_cast_delete(
    series_id: int,
    person_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    await models.Series_cast.delete(
        series_id=series_id,
        person_id=person_id,
    )


@router.get('', response_model=schemas.Page_cursor_result[schemas.Series_cast_person])
async def series_cast_get(
    series_id: int,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Series_cast).where(
        models.Series_cast.series_id == series_id,
    ).order_by(
        models.Series_cast.order,
    )
    p = await utils.sqlalchemy.paginate_cursor(
        session=session,
        query=query,
        page_query=page_query,
    )
    p.items = [schemas.Series_cast_person.from_orm(row[0]) for row in p.items]
    return p