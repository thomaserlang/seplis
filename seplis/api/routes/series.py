from urllib.parse import urljoin
from fastapi import APIRouter, Depends, HTTPException, Security, Request, UploadFile, Form
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession, httpx_client
from ..database import database
from .. import models, schemas, constants
from ... import logger, utils, config

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
    return await models.Series.save(series_id=series_id, series=data, patch=False)


@router.patch('/{series_id}', response_model=schemas.Series)
async def patch_series(
    series_id: int,
    data: schemas.Series_update,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_EDIT_SHOW)]),
):
    return await models.Series.save(series_id=series_id, series=data, patch=True)


@router.delete('/{series_id}', status_code=204)
async def delete_series(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_DELETE_SHOW)]),
):
    await models.Series.delete(series_id)


@router.delete('/{series_id}/update', status_code=204)
async def request_update(series_id: int):
    await database.redis_queue.enqueue_job('update_series', series_id)


@router.get('/{series_id}/episodes', response_model=schemas.Page_result[schemas.Episode])
async def get_episodes(
    series_id: int,
    request: Request,
    season: int | None = None,
    page_query: schemas.Page_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
    )
    if season:
        query = query.where(models.Episode.season == season)
    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    p.items = [schemas.Episode.from_orm(episode) for episode in p.items]
    return p


@router.get('/{series_id}/episodes/{number}', response_model=schemas.Episode)
async def get_episode(
    series_id: int,
    number: int,
    session: AsyncSession = Depends(get_session),
):
    episode = await session.scalar(sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
    if not episode:
        raise HTTPException(404, 'Unknown episode')
    return schemas.Episode.from_orm(episode)


@router.delete('/{series_id}/episodes/{number}', status_code=204)
async def delete_episode(
    series_id: int,
    number: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_DELETE_SHOW)]),
):
    await session.execute(sa.delete(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))


@router.post('/{series_id}/images', response_model=schemas.Image, status_code=201)
async def create_image(
    series_id: int,
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
        relation_type = 'series',
        relation_id = series_id,
        external_name = external_name,
        external_id = external_id,
        height = file['height'],
        width = file['width'],
        hash = file['hash'],
        type = type,
    ))
    image = await session.scalar(sa.select(models.Image).where(models.Image.id == r.lastrowid))
    return schemas.Image.from_orm(image)


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


@router.get('/{series_id}/images', response_model=schemas.Page_result[schemas.Image])
async def get_images(
    series_id: int,
    request: Request,
    type: schemas.IMAGE_TYPES | None = None,
    page_query: schemas.Page_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Image).where(
        models.Image.relation_type == 'series',
        models.Image.relation_id == series_id,
    )
    if type:
        query = query.where(models.Image.type == type)
    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    p.items = [schemas.Image.from_orm(image) for image in p.items]
    return p
