import sqlalchemy as sa
from fastapi import Depends, Form, Security, UploadFile

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.post(
    '/{series_id}/images',
    response_model=schemas.Image,
    status_code=201,
    description="""
            **Scope required:** `series:manage_images`
            """,
)
async def create_image(
    series_id: int,
    image: UploadFile,
    external_name: str | None = Form(default=None, min_length=1, max_length=50),
    external_id: str | None = Form(default=None, min_length=1, max_length=50),
    type: schemas.IMAGE_TYPES = Form(),
    user: User_authenticated = Security(authenticated, scopes=['series:manage_images']),
):
    image_data = schemas.Image_import(
        external_name=external_name,
        external_id=external_id,
        file=image,
        type=type,
    )
    return await models.MImage.save(
        relation_type='series',
        relation_id=series_id,
        image_data=image_data,
    )


@router.delete(
    '/{series_id}/images/{image_id}',
    status_code=204,
    description="""
            **Scope required:** `series:manage_images`
            """,
)
async def delete_image(
    series_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
    user: User_authenticated = Security(authenticated, scopes=['series:manage_images']),
) -> None:
    await session.execute(
        sa.update(models.MSeries)
        .values(poster_image_id=None)
        .where(
            models.MSeries.id == series_id,
            models.MSeries.poster_image_id == image_id,
        )
    )
    await session.execute(
        sa.delete(models.MImage).where(
            models.MImage.relation_type == 'series',
            models.MImage.relation_id == series_id,
            models.MImage.id == image_id,
        )
    )
    await session.commit()


@router.get(
    '/{series_id}/images', response_model=schemas.Page_cursor_total_result[schemas.Image]
)
async def get_images(
    series_id: int,
    type: schemas.IMAGE_TYPES | None = None,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.MImage).where(
        models.MImage.relation_type == 'series',
        models.MImage.relation_id == series_id,
    )
    if type:
        query = query.where(models.MImage.type == type)
    p = await utils.sqlalchemy.paginate_cursor_total(
        session=session, query=query, page_query=page_query
    )
    p.items = [schemas.Image.model_validate(row.MImage) for row in p.items]
    return p
