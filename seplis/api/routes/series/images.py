import sqlalchemy as sa
from fastapi import Depends, Security, UploadFile, Form
from .... import utils
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router


@router.post('/{series_id}/images', response_model=schemas.Image, status_code=201,
            description='''
            **Scope required:** `series:manage_images`
            ''')
async def create_image(
    series_id: int,
    image: UploadFile,
    external_name: str | None = Form(
        default=None, min_length=1, max_length=50),
    external_id: str | None = Form(default=None, min_length=1, max_length=50),
    type: schemas.IMAGE_TYPES = Form(),
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['series:manage_images']),
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


@router.delete('/{series_id}/images/{image_id}', status_code=204,
            description='''
            **Scope required:** `series:manage_images`
            ''')
async def delete_image(
    series_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['series:manage_images']),
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
    p.items = [schemas.Image.model_validate(row.Image) for row in p.items]
    return p
