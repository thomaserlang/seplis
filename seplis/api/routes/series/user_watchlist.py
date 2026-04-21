from fastapi import Security

from ... import models, schemas
from ...dependencies import authenticated
from .router import router


@router.get(
    '/{series_id}/watchlist',
    response_model=schemas.Series_watchlist,
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def series_watchlist(
    series_id: int,
    user: User_authenticated = Security(authenticated, scopes=['user:view_lists']),
):
    return await models.MSeriesWatchlist.get(series_id=series_id, user_id=user.id)


@router.put(
    '/{series_id}/watchlist',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def series_add_to_watchlist(
    series_id: int,
    user: User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
) -> None:
    await models.MSeriesWatchlist.add(series_id=series_id, user_id=user.id)


@router.delete(
    '/{series_id}/watchlist',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def series_remove_from_watchlist(
    series_id: int,
    user: User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
) -> None:
    await models.MSeriesWatchlist.remove(series_id=series_id, user_id=user.id)
