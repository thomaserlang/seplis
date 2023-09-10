import sqlalchemy as sa
from fastapi import Depends, Security
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .... import utils
from .router import router


@router.put('/{series_id}/episodes/{episode_number}/cast', status_code=204,
            description='''
            **Scope required:** `series:edit`
            ''')
async def episode_cast_add(
    series_id: int,
    episode_number: int,
    data: schemas.Episode_cast_person_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=['series:edit']),
):
    data.series_id = series_id
    data.episode_number = episode_number
    await models.Episode_cast.save(data=data)


@router.delete('/{series_id}/episodes/{episode_number}/cast/{person_id}', status_code=204,
            description='''
            **Scope required:** `series:edit`
            ''')
async def episode_cast_delete(
    series_id: int,
    episode_number: int,
    person_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['series:edit']),
):
    await models.Episode_cast.delete(
        series_id=series_id,
        episode_number=episode_number,
        person_id=person_id,
    )


@router.get('/{series_id}/episodes/{episode_number}/cast', 
            response_model=schemas.Page_cursor_result[schemas.Episode_cast_person],
            description='''
            **Scope required:** `series:edit`
            ''')
async def episode_cast_get(
    series_id: int,
    episode_number: int,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Episode_cast).where(
        models.Episode_cast.series_id == series_id,
        models.Episode_cast.episode_number == episode_number,
    ).order_by(
        models.Episode_cast.order,
    )
    p = await utils.sqlalchemy.paginate_cursor(
        session=session,
        query=query,
        page_query=page_query,
    )
    p.items = [schemas.Episode_cast_person.model_validate(row[0]) for row in p.items]
    return p