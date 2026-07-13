from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_user_actions import (
    add_series_watchlist,
    get_series_watchlist,
    remove_series_watchlist,
)
from ..schemas.series_schemas import SeriesWatchlist

router = APIRouter()


@router.get(
    '/{series_id}/watchlist',
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def series_watchlist_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
) -> SeriesWatchlist:
    return await get_series_watchlist(series_id=series_id, user_id=user.id)


@router.put(
    '/{series_id}/watchlist',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def series_add_to_watchlist_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await add_series_watchlist(series_id=series_id, user_id=user.id)


@router.delete(
    '/{series_id}/watchlist',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def series_remove_from_watchlist_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await remove_series_watchlist(series_id=series_id, user_id=user.id)
