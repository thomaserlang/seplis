from fastapi import Depends, Security, UploadFile, Form
import sqlalchemy as sa
from .... import utils
from ... import models, schemas
from ...dependencies import authenticated, get_session, AsyncSession
from .router import router


@router.post('/{movie_id}/images', response_model=schemas.Image, status_code=201,
            description='''
            **Scope required:** `movie:manage_images`
            ''')
async def create_image(
    movie_id: int,
    image: UploadFile,
    type: schemas.IMAGE_TYPES = Form(),
    external_name: str = Form(default=None, min_length=1, max_length=50),
    external_id: str = Form(default=None, min_length=1, max_length=50),
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:manage_images']),
):
    image_data = schemas.Image_import(
        external_name=external_name,
        external_id=external_id,
        file=image,
        type=type,
    )
    return await models.Image.save(
        relation_type='movie',
        relation_id=movie_id,
        image_data=image_data,
    )


@router.delete('/{movie_id}/images/{image_id}', status_code=204,
            description='''
            **Scope required:** `movie:manage_images`
            ''')
async def delete_image(
    movie_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:manage_images']),
):
    await session.execute(sa.update(models.Movie).values(poster_image_id=None).where(
        models.Movie.id == movie_id,
        models.Movie.poster_image_id == image_id,
    ))
    await session.execute(sa.delete(models.Image).where(
        models.Image.relation_type == 'movie',
        models.Image.relation_id == movie_id,
        models.Image.id == image_id,
    ))
    await session.commit()


@router.get('/{movie_id}/images', response_model=schemas.Page_cursor_total_result[schemas.Image],
            description='''
            **Scope required:** `movie:manage_images`
            ''')
async def get_images(
    movie_id: int,
    type: schemas.IMAGE_TYPES | None = None,
    page_query: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Image).where(
        models.Image.relation_type == 'movie',
        models.Image.relation_id == movie_id,
    )
    if type:
        query = query.where(models.Image.type == type)
    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [schemas.Image.model_validate(row.Image) for row in p.items]
    return p
