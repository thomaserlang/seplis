from fastapi import Security
from ...dependencies import authenticated
from ... import models, schemas
from .router import router


@router.get('/{series_id}/watchlist', response_model=schemas.Series_watchlist,
            description='''
            **Scope required:** `user:view_lists`
            ''')
async def series_watchlist(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
):
    return await models.Series_watchlist.get(series_id=series_id, user_id=user.id)
    

@router.put('/{series_id}/watchlist', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def series_add_to_watchlist(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Series_watchlist.add(series_id=series_id, user_id=user.id)


@router.delete('/{series_id}/watchlist', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def series_remove_from_watchlist(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Series_watchlist.remove(series_id=series_id, user_id=user.id)