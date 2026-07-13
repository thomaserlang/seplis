from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_cast_actions import (
    add_series_cast,
    delete_series_cast,
    get_series_cast,
)
from ..schemas.series_cast_schemas import SeriesCastPerson, SeriesCastPersonCreate

router = APIRouter()


@router.put(
    '/{series_id}/cast',
    status_code=204,
    description="""
            **Scope required:** `series:edit`
            """,
)
async def series_cast_add_route(
    series_id: int,
    cast_member: SeriesCastPersonCreate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> None:
    await add_series_cast(series_id=series_id, data=cast_member)


@router.delete(
    '/{series_id}/cast',
    status_code=204,
    description="""
            **Scope required:** `series:edit`
            """,
)
async def series_cast_delete_route(
    series_id: int,
    person_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> None:
    await delete_series_cast(series_id=series_id, person_id=person_id)


@router.get(
    '/{series_id}/cast',
    description="""
            **Scope required:** `series:edit`
            """,
)
async def series_cast_get_route(
    series_id: int,
    page_query: Annotated[PageCursorQuery, Depends()],
    order_le: int | None = None,
    order_ge: int | None = None,
) -> PageCursor[SeriesCastPerson]:
    return await get_series_cast(
        series_id=series_id,
        order_le=order_le,
        order_ge=order_ge,
        page_query=page_query,
    )
