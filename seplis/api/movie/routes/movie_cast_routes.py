from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.dependencies import authenticated
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.user import UserAuthenticated

from ..actions.movie_cast_actions import (
    delete_movie_cast,
    get_movie_cast,
    save_movie_cast,
)
from ..schemas.movie_cast_schemas import MovieCastPerson, MovieCastPersonCreate

router = APIRouter()


@router.put('/{movie_id}/cast', status_code=204)
async def movie_cast_add_route(
    movie_id: int,
    data: MovieCastPersonCreate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:edit'])],
) -> None:
    await save_movie_cast(movie_id=movie_id, data=data)


@router.delete('/{movie_id}/cast', status_code=204)
async def movie_cast_delete_route(
    movie_id: int,
    person_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['movie:edit'])],
) -> None:
    await delete_movie_cast(movie_id=movie_id, person_id=person_id)


@router.get('/{movie_id}/cast')
async def movie_cast_get_route(
    movie_id: int,
    page_query: Annotated[PageCursorQuery, Depends()],
    order_le: int | None = None,
    order_ge: int | None = None,
) -> PageCursor[MovieCastPerson]:
    return await get_movie_cast(
        movie_id=movie_id,
        page_query=page_query,
        order_le=order_le,
        order_ge=order_ge,
    )
