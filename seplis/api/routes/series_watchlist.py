from fastapi import APIRouter, Security
from ..dependencies import authenticated
from .. import models, schemas, constants

router = APIRouter(prefix='/2/series/{series_id}/watchlist')


@router.get('', response_model=schemas.Series_watchlist)
async def series_watchlist(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
):
    return await models.Series_watchlist.get(series_id=series_id, user_id=user.id)
    

@router.put('', status_code=204)
async def series_add_to_watchlist(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Series_watchlist.add(series_id=series_id, user_id=user.id)


@router.delete('', status_code=204)
async def series_remove_from_watchlist(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_lists']),
):
    await models.Series_watchlist.remove(series_id=series_id, user_id=user.id)