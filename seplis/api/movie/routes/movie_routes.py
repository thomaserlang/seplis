from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.dependencies import (
    authenticated,
    get_current_user_no_raise,
    get_expand,
)
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.user import UserAuthenticated

from ..actions.movie_actions import (
    create_movie,
    delete_movie,
    get_movie,
    get_movies,
    patch_movie,
    request_movie_update,
    update_movie,
)
from ..schemas.movie_schemas import Movie, MovieCreate, MovieUpdate
from ..types.movie_filter_types import MovieQueryFilterDep

router = APIRouter()


@router.get('')
async def get_movies_route(
    page_cursor: Annotated[PageCursorQuery, Depends()],
    filter_query: MovieQueryFilterDep,
) -> PageCursor[Movie]:
    return await get_movies(page_cursor=page_cursor, filter_query=filter_query)


@router.get('/{movie_id}')
async def get_movie_route(
    movie_id: int,
    expand: Annotated[list[str] | None, Depends(get_expand)],
    user: Annotated[UserAuthenticated | None, Depends(get_current_user_no_raise)],
) -> Movie:
    return await get_movie(movie_id=movie_id, expand=expand, user=user)


@router.post('', status_code=201)
async def create_movie_route(
    data: MovieCreate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:create'])],
) -> Movie:
    return await create_movie(data=data)


@router.put('/{movie_id}')
async def update_movie_route(
    movie_id: int,
    data: MovieUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:edit'])],
) -> Movie:
    return await update_movie(movie_id=movie_id, data=data)


@router.patch('/{movie_id}')
async def patch_movie_route(
    movie_id: int,
    data: MovieUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:edit'])],
) -> Movie:
    return await patch_movie(movie_id=movie_id, data=data)


@router.delete('/{movie_id}', status_code=204)
async def delete_movie_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:delete'])],
) -> None:
    await delete_movie(movie_id=movie_id)


@router.post('/{movie_id}/update', status_code=204)
async def request_update_route(
    movie_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:update'])],
) -> None:
    await request_movie_update(movie_id=movie_id)
