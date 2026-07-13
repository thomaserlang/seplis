from typing import Annotated

from fastapi import APIRouter, Security

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_user_actions import (
    delete_series_rating,
    get_series_rating,
    update_series_rating,
)
from ..schemas.series_schemas import SeriesUserRating, SeriesUserRatingUpdate

router = APIRouter()


@router.get(
    '/{series_id}/user-rating',
    description="""
            **Scope required:** `user:view_ratings`
            """,
)
async def get_rating_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:view_ratings'])
    ],
) -> SeriesUserRating:
    return await get_series_rating(series_id=series_id, user_id=user.id)


@router.put(
    '/{series_id}/user-rating',
    status_code=204,
    description="""
            **Scope required:** `user:manage_ratings`
            """,
)
async def update_rating_route(
    series_id: int,
    data: SeriesUserRatingUpdate,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_ratings'])
    ],
) -> None:
    await update_series_rating(series_id=series_id, user_id=user.id, data=data)


@router.delete(
    '/{series_id}/user-rating',
    status_code=204,
    description="""
            **Scope required:** `user:manage_ratings`
            """,
)
async def delete_rating_route(
    series_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_ratings'])
    ],
) -> None:
    await delete_series_rating(series_id=series_id, user_id=user.id)
