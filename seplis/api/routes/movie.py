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
    return await models.Movie.save(movie_id=movie_id, movie_data=data, patch=False)


@router.patch('/{movie_id}', response_model=schemas.Movie)
async def patch_movie(
    movie_id: int,
    data: schemas.Movie_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    return await models.Movie.save(movie_id=movie_id, movie_data=data, patch=True)


@router.delete('/{movie_id}', status_code=204)
async def delete_movie(
    movie_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_DELETE_SHOW)]),
):
    await models.Movie.delete(movie_id=movie_id)


@router.delete('/{movie_id}/update', status_code=204)
async def request_update(movie_id: int):
    await database.redis_queue.enqueue_job('update_series', movie_id)
    

@router.post('/{movie_id}/images', response_model=schemas.Image, status_code=201)
async def create_image(
    movie_id: int,
    image: UploadFile,
    external_name: str = Form(default=None, min_length=1, max_length=50),
    external_id: str = Form(default=None, min_length=1, max_length=50),
    type: str = Form(min_length=6, max_length=7, description='Must be either: poster or backdrop'),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    async def upload_bytes():
        while content := await image.read(128*1024):
            yield content

    if type not in ('poster', 'backdrop'):
        raise HTTPException(400, '`type` must be either: poster or backdrop')

    r = await httpx_client.put(
        urljoin(config.data.api.storitch, '/store/session'), 
        headers={
            'storitch-json': utils.json_dumps({
                'finished': True,
                'filename': image.filename,
            }),
            'content-type': 'application/octet-stream',
        },
        content=upload_bytes()
    )
    if r.status_code != 200:
        logger.error(f'File upload failed: {r.content}')
        raise HTTPException(500, 'Unable to store the image')
    
    file = utils.json_loads(r.content)
    
    if file['type'] != 'image':
        raise HTTPException(400, 'File must be an image')

    if type == constants.IMAGE_TYPE_POSTER:
        if round(file['width']/file['height'], 2) not in constants.ASPECT_RATIO_POSTER:
            raise HTTPException(400, f'Image must have the following aspect ratio: {constants.ASPECT_RATIO_POSTER}')

    if external_name or external_id:
        q = await session.scalar(sa.select(models.Image.id).where(
            models.Image.external_name == external_name,
            models.Image.external_id == external_id,
        ))
        if q:
            raise HTTPException(400, f'An image with `external_name`: {external_name} and `external_id`: {external_id} already exists')

    r = await session.execute(sa.insert(models.Image).values(
        relation_type = 'movie',
        relation_id = movie_id,
        external_name = external_name,
        external_id = external_id,
        height = file['height'],
        width = file['width'],
        hash = file['hash'],
        type = type,
    ))
    image = await session.scalar(sa.select(models.Image).where(models.Image.id == r.lastrowid))
    return schemas.Image.from_orm(image)


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


@router.get('/{movie_id}/images', response_model=schemas.Page_result[schemas.Image])
async def get_images(
    movie_id: int,
    request: Request,
    type: schemas.IMAGE_TYPES | None = None,
    page_query: schemas.Page_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Image).where(
        models.Image.relation_type == 'movie',
        models.Image.relation_id == movie_id,
    )
    if type:
        query = query.where(models.Image.type == type)
    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    p.items = [schemas.Image.from_orm(image) for image in p.items]
    return p