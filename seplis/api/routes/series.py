from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, Form
import sqlalchemy as sa
from ..dependencies import authenticated, get_session, AsyncSession
from ..database import database
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/series')

@router.get('/{series_id}', response_model=schemas.Series)
async def get_series(
    series_id: int, 
    session: AsyncSession=Depends(get_session),
):
    series = await session.scalar(sa.select(models.Series).where(models.Series.id == series_id))
    if not series:
        raise HTTPException(404, 'Unknown series')
    return schemas.Series.from_orm(series)


@router.get('/externals/{external_name}/{external_id}', response_model=schemas.Series)
async def get_series_by_external(
    external_name: str,
    external_id: str, 
    session: AsyncSession=Depends(get_session),
):
    series = await session.scalar(sa.select(models.Series).where(
        models.Series_external.title == external_name,
        models.Series_external.value == external_id,
        models.Series.id == models.Series_external.series_id,
    ))
    if not series:
        raise HTTPException(404, 'Unknown series')
    return schemas.Series.from_orm(series)


@router.post('', status_code=201, response_model=schemas.Series)
async def create_series(
    data: schemas.Series_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    series = await models.Series.save(data, series_id=None, patch=False)
    await database.redis_queue.enqueue_job('update_series', int(series.id))
    return series


@router.put('/{series_id}', response_model=schemas.Series)
async def update_series(
    series_id: int,
    data: schemas.Series_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    return await models.Series.save(series_id=series_id, data=data, patch=False)


@router.patch('/{series_id}', response_model=schemas.Series)
async def patch_series(
    series_id: int,
    data: schemas.Series_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    return await models.Series.save(series_id=series_id, data=data, patch=True)


@router.delete('/{series_id}', status_code=204)
async def delete_series(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_DELETE_SHOW)]),
):
    await models.Series.delete(series_id)


@router.post('/{series_id}/update', status_code=204)
async def request_update(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    await database.redis_queue.enqueue_job('update_series', series_id)


@router.post('/{series_id}/images', response_model=schemas.Image, status_code=201)
async def create_image(
    series_id: int,
    image: UploadFile,
    external_name: str | None = Form(default=None, min_length=1, max_length=50),
    external_id: str | None = Form(default=None, min_length=1, max_length=50),
    type: schemas.IMAGE_TYPES = Form(),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    image_data = schemas.Image_import(
        external_name=external_name,
        external_id=external_id,
        file=image,
        type=type,
    )
    return await models.Image.save(
        relation_type='series',
        relation_id=series_id,
        image_data=image_data,
    )


@router.delete('/{series_id}/images/{image_id}', status_code=204)
async def delete_image(
    series_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    await session.execute(sa.update(models.Series).values(poster_image_id=None).where(
        models.Series.id == series_id,
        models.Series.poster_image_id == image_id,
    ))
    await session.execute(sa.delete(models.Image).where(
        models.Image.relation_type == 'series',
        models.Image.relation_id == series_id,
        models.Image.id == image_id,
    ))
    await session.commit()


@router.get('/{series_id}/images', response_model=schemas.Page_cursor_total_result[schemas.Image])
async def get_images(
    series_id: int,
    type: schemas.IMAGE_TYPES | None = None,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Image).where(
        models.Image.relation_type == 'series',
        models.Image.relation_id == series_id,
    )
    if type:
        query = query.where(models.Image.type == type)
    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [schemas.Image.from_orm(row.Image) for row in p.items]
    return p
