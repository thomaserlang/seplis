from urllib.parse import urljoin
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, Form, Request
import sqlalchemy as sa

from seplis.api import constants
from ..dependencies import authenticated, get_session, AsyncSession, httpx_client
from .. import models, schemas
from ..database import database
from ... import config, utils, logger

router = APIRouter(prefix='/2/movies')

@router.get('/{movie_id}', response_model=schemas.Movie)
async def get_movie(
    movie_id: int, 
    session: AsyncSession=Depends(get_session),
):
    movie = await session.scalar(sa.select(models.Movie).where(models.Movie.id == movie_id))
    if not movie:
        raise HTTPException(404, 'Unknown movie')
    return movie


@router.post('', status_code=201, response_model=schemas.Movie)
async def create_movie(
    data: schemas.Movie_create,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    movie = await models.Movie.save(data, movie_id=None, patch=False)
    await database.redis_queue.enqueue_job('update_movie', int(movie.id))
    return movie


@router.put('/{movie_id}', response_model=schemas.Movie)
async def update_movie(
    movie_id: int,
    data: schemas.Movie_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    return await models.Movie.save(movie_id=movie_id, data=data, patch=False)


@router.patch('/{movie_id}', response_model=schemas.Movie)
async def patch_movie(
    movie_id: int,
    data: schemas.Movie_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    return await models.Movie.save(movie_id=movie_id, data=data, patch=True)


@router.delete('/{movie_id}', status_code=204)
async def delete_movie(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_DELETE_SHOW)]),
):
    await models.Movie.delete(movie_id=movie_id)


@router.post('/{movie_id}/update', status_code=204)
async def request_update(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    await database.redis_queue.enqueue_job('update_movie', movie_id)
    

@router.post('/{movie_id}/images', response_model=schemas.Image, status_code=201)
async def create_image(
    movie_id: int,
    image: UploadFile,
    type: schemas.IMAGE_TYPES = Form(),
    external_name: str = Form(default=None, min_length=1, max_length=50),
    external_id: str = Form(default=None, min_length=1, max_length=50),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
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


@router.delete('/{movie_id}/images/{image_id}', status_code=204)
async def delete_image(
    movie_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
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


@router.get('/{movie_id}/images', response_model=schemas.Page_cursor_total_result[schemas.Image])
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
    p.items = [schemas.Image.from_orm(row.Image) for row in p.items]
    return p