import sqlalchemy as sa
from fastapi import Depends, Form, Security, UploadFile

from .... import utils
from ... import models, schemas
from ...dependencies import AsyncSession, UserAuthenticated, authenticated, get_session
from .router import router


@router.post(
    '/{movie_id}/images',
    response_model=schemas.Image,
    status_code=201,
    description="""
            **Scope required:** `movie:manage_images`
            """,
)
async def create_image(
    movie_id: int,
    image: UploadFile,
    type: schemas.IMAGE_TYPES = Form(),
    external_name: str = Form(default=None, min_length=1, max_length=50),
    external_id: str = Form(default=None, min_length=1, max_length=50),
    user: UserAuthenticated = Security(authenticated, scopes=['movie:manage_images']),
):
    image_data = schemas.Image_import(
        external_name=external_name,
        external_id=external_id,
        file=image,
        type=type,
    )
    return await models.MImage.save(
        relation_type='movie',
        relation_id=movie_id,
        image_data=image_data,
    )


@router.delete(
    '/{movie_id}/images/{image_id}',
    status_code=204,
    description="""
            **Scope required:** `movie:manage_images`
            """,
)
async def delete_image(
    movie_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
    user: UserAuthenticated = Security(authenticated, scopes=['movie:manage_images']),
) -> None:
    await session.execute(
        sa.update(models.MMovie)
        .values(poster_image_id=None)
        .where(
            models.MMovie.id == movie_id,
            models.MMovie.poster_image_id == image_id,
        )
    )
    await session.execute(
        sa.delete(models.MImage).where(
            models.MImage.relation_type == 'movie',
            models.MImage.relation_id == movie_id,
            models.MImage.id == image_id,
        )
    )
    await session.commit()


@router.get(
    '/{movie_id}/images',
    response_model=schemas.Page_cursor_total_result[schemas.Image],
    description="""
            **Scope required:** `movie:manage_images`
            """,
)
async def get_images(
    movie_id: int,
    type: schemas.IMAGE_TYPES | None = None,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.MImage).where(
        models.MImage.relation_type == 'movie',
        models.MImage.relation_id == movie_id,
    )
    if type:
        query = query.where(models.MImage.type == type)
    p = await utils.sqlalchemy.paginate_cursor_total(
        session=session, query=query, page_query=page_query
    )
    p.items = [schemas.Image.model_validate(row.MImage) for row in p.items]
    return p
