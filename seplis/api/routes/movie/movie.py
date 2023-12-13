from fastapi import Depends, HTTPException, Security
import sqlalchemy as sa
from ....api.filter.movies.query_filter_schema import Movie_query_filter
from ... import models, schemas
from ...dependencies import authenticated, get_current_user_no_raise, get_expand, get_session, AsyncSession
from ...database import database
from ...filter.movies import filter_movies
from ...expand.movie import expand_movies
from .router import router


@router.get('', response_model=schemas.Page_cursor_result[schemas.Movie])
async def get_movies(
    page_cursor: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
    filter_query: Movie_query_filter = Depends(),
):
    query = sa.select(models.Movie)
    p = await filter_movies(
        query=query,
        session=session,
        filter_query=filter_query,
        page_cursor=page_cursor,
    )
    return p


@router.get('/{movie_id}', response_model=schemas.Movie)
async def get_movie(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Depends(
        get_current_user_no_raise),
):
    movie = await session.scalar(sa.select(models.Movie).where(models.Movie.id == movie_id))
    if not movie:
        raise HTTPException(404, 'Unknown movie')
    await expand_movies(movies=[movie], user=user, expand=expand)
    return movie


@router.post('', status_code=201, response_model=schemas.Movie,
            description='''
            **Scope required:** `movie:create`
            ''')
async def create_movie(
    data: schemas.Movie_create,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:create']),
):
    movie = await models.Movie.save(data, movie_id=None, patch=False)
    await database.redis_queue.enqueue_job('update_movie', int(movie.id))
    return movie


@router.put('/{movie_id}', response_model=schemas.Movie,
            description='''
            **Scope required:** `movie:edit`
            ''')
async def update_movie(
    movie_id: int,
    data: schemas.Movie_update,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:edit']),
):
    return await models.Movie.save(movie_id=movie_id, data=data, patch=False)


@router.patch('/{movie_id}', response_model=schemas.Movie,
            description='''
            **Scope required:** `movie:edit`
            ''')
async def patch_movie(
    movie_id: int,
    data: schemas.Movie_update,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:edit']),
):
    return await models.Movie.save(movie_id=movie_id, data=data, patch=True)


@router.delete('/{movie_id}', status_code=204,
            description='''
            **Scope required:** `movie:delete`
            ''')
async def delete_movie(
    movie_id: int,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:delete']),
):
    await models.Movie.delete(movie_id=movie_id)


@router.post('/{movie_id}/update', status_code=204,
            description='''
            **Scope required:** `movie:update`
            ''')
async def request_update(
    movie_id: int,
    user: schemas.User_authenticated = Security(
        authenticated, scopes=['movie:update']),
):
    await database.redis_queue.enqueue_job('update_movie', movie_id)