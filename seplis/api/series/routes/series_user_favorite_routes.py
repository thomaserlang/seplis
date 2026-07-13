from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_user_actions import (
    add_series_favorite,
    get_series_favorite,
    remove_series_favorite,
)
from ..schemas.series_schemas import SeriesFavorite

router = APIRouter()


@router.get(
    '/{series_id}/favorite',
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def series_favorite_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_lists'])
    ],
) -> SeriesFavorite:
    return await get_series_favorite(series_id=series_id, user_id=user.id)


@router.put(
    '/{series_id}/favorite',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def series_add_to_favorites_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await add_series_favorite(series_id=series_id, user_id=user.id)


@router.delete(
    '/{series_id}/favorite',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def series_remove_from_favorites_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_lists'])
    ],
) -> None:
    await remove_series_favorite(series_id=series_id, user_id=user.id)
