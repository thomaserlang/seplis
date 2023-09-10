from fastapi import APIRouter, Security
from ...dependencies import authenticated
from ... import models, schemas
from .router import router

@router.get('/{series_id}/favorite', response_model=schemas.Series_favorite,
            description='''
            **Scope required:** `user:view_lists`
            ''')
async def series_favorite(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
):
    return await models.Series_favorite.get(series_id=series_id, user_id=user.id)
    

@router.put('/{series_id}/favorite', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def series_add_to_favorites(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Series_favorite.add(series_id=series_id, user_id=user.id)


@router.delete('/{series_id}/favorite', status_code=204,
            description='''
            **Scope required:** `user:manage_lists`
            ''')
async def series_remove_from_favorites(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Series_favorite.remove(series_id=series_id, user_id=user.id)