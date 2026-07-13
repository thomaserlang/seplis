from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import (
    authenticated,
    get_current_user_no_raise,
    get_expand,
)
from ...user import UserAuthenticated
from ..actions.series_actions import (
    create_series,
    delete_series,
    get_series,
    get_series_by_external,
    get_series_one,
    patch_series,
    request_series_update,
    update_series,
)
from ..schemas.series_schemas import Series, SeriesCreate, SeriesUpdate
from ..types.series_filter_types import SeriesQueryFilterDep

router = APIRouter()


@router.get('')
async def get_series_route(
    page_cursor: Annotated[PageCursorQuery, Depends()],
    filter_query: SeriesQueryFilterDep,
) -> PageCursor[Series]:
    return await get_series(page_cursor=page_cursor, filter_query=filter_query)


@router.get('/{series_id}')
async def get_series_one_route(
    series_id: int,
    expand: Annotated[list[str] | None, Depends(get_expand)],
    user: Annotated[UserAuthenticated | None, Depends(get_current_user_no_raise)],
) -> Series:
    return await get_series_one(series_id=series_id, expand=expand, user=user)


@router.get('/externals/{external_name}/{external_id}')
async def get_series_by_external_route(
    external_name: str,
    external_id: str,
) -> Series:
    return await get_series_by_external(
        external_name=external_name, external_id=external_id
    )


@router.post(
    '',
    status_code=201,
    description="""
            **Scope required:** `series:create`
            """,
)
async def create_series_route(
    data: SeriesCreate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:create'])],
) -> Series:
    return await create_series(data)


@router.put(
    '/{series_id}',
    description="""
            **Scope required:** `series:edit`
            """,
)
async def update_series_route(
    series_id: int,
    data: SeriesUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> Series:
    return await update_series(series_id=series_id, data=data)


@router.patch(
    '/{series_id}',
    description="""
            **Scope required:** `series:edit`
            """,
)
async def patch_series_route(
    series_id: int,
    data: SeriesUpdate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> Series:
    return await patch_series(series_id=series_id, data=data)


@router.delete(
    '/{series_id}',
    status_code=204,
    description="""
            **Scope required:** `series:delete`
            """,
)
async def delete_series_route(
    series_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:delete'])],
) -> None:
    await delete_series(series_id)


@router.post(
    '/{series_id}/update',
    status_code=204,
    description="""
            **Scope required:** `series:update`
            """,
)
async def request_update_route(
    series_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:update'])],
) -> None:
    await request_series_update(series_id)
