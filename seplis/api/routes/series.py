from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, Form
import sqlalchemy as sa

from seplis.api.expand.series import expand_series
from ... import utils
from ..dependencies import authenticated, get_current_user_no_raise, get_expand, get_session, AsyncSession
from ..database import database
from .. import models, schemas, constants, exceptions

router = APIRouter(prefix='/2/series')


@router.get('', response_model=schemas.Page_cursor_result[schemas.Series])
async def get_series(
    expand: list[schemas.SERIES_EXPAND] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise),
    page_cursor: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
    user_can_watch: bool = None,
    user_following: bool = None,
    user_has_watched: bool = None,
    filter_query: schemas.Series_user_query_filter = Depends(schemas.Series_user_query_filter),
    sort: schemas.SERIES_USER_SORT_TYPE = 'popularity_desc',
):
    query = sa.select(models.Series)
    
    if user_can_watch:
        if not user:
            raise exceptions.Not_signed_in_exception()
        query = query.where(
            models.Play_server_access.user_id == user.id,
            models.Play_server_episode.play_server_id == models.Play_server_access.play_server_id,
            models.Play_server_episode.series_id == models.Series.id,
            models.Play_server_episode.episode_number == 1,
        )

    if user_following or sort.startswith('user_followed_at'):
        if not user:
            raise exceptions.Not_signed_in_exception()
        query = query.where(
            models.Series_follower.user_id == user.id,
            models.Series_follower.series_id == models.Series.id,
        )

    if user_has_watched or sort.startswith('user_last_episode_watched_at'):
        if not user:
            raise exceptions.Not_signed_in_exception()
        query = query.where(
            models.Episode_last_watched.user_id == user.id,
            models.Series.id == models.Episode_last_watched.series_id,
            models.Episode_watched.user_id ==  models.Episode_last_watched.user_id,
            models.Episode_watched.series_id ==  models.Episode_last_watched.series_id,
            models.Episode_watched.episode_number == models.Episode_last_watched.episode_number,
        )

    if filter_query:
        if filter_query.genre_id:
            if len(filter_query.genre_id) == 1:
                query = query.where(
                    models.Series_genre.genre_id == filter_query.genre_id[0],
                    models.Series.id == models.Series_genre.series_id,
                )
            else:                
                query = query.where(
                    models.Series_genre.genre_id.in_(filter_query.genre_id),
                    models.Series.id == models.Series_genre.series_id,
                ).group_by(models.Series.id)

    direction = sa.asc if sort.endswith('_asc') else sa.desc
    if sort.startswith('user_rating'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series_user_rating.rating, -1)),
            direction(models.Series.id),
        )
    elif sort.startswith('user_followed_at'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series_follower.created_at, -1)),
            direction(models.Series.id),
        )
    elif sort.startswith('user_last_episode_watched_at'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Episode_watched.watched_at, -1)),
            direction(models.Series.id),
        )
    elif sort.startswith('rating'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series.rating, -1)),
            direction(models.Series.id),
        )
    elif sort.startswith('popularity_desc'):
        query = query.order_by(
            direction(sa.func.coalesce(models.Series.popularity, -1)),
            direction(models.Series.id),
        )

    p = await utils.sqlalchemy.paginate_cursor(
        session=session, 
        query=query,
        page_query=page_cursor,
    )
    p.items = [schemas.Series.from_orm(row[0]) for row in p.items]
    await expand_series(series=p.items, user=user, expand=expand, session=session)
    return p


@router.get('/{series_id}', response_model=schemas.Series)
async def get_series_one(
    series_id: int, 
    session: AsyncSession=Depends(get_session),
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise),
):
    series = await session.scalar(sa.select(models.Series).where(models.Series.id == series_id))
    if not series:
        raise HTTPException(404, 'Unknown series')
    s = schemas.Series.from_orm(series)
    await expand_series(series=[s], user=user, expand=expand, session=session)
    return s


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
