from fastapi import APIRouter, Security
from ..dependencies import authenticated
from .. import models, schemas, constants

router = APIRouter(prefix='/2/series/{series_id}/favorite')


@router.get('', response_model=schemas.Series_favorite)
async def series_favorite(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    return await models.Series_favorite.get(series_id=series_id, user_id=user.id)
    

@router.put('', status_code=204)
async def series_add_to_favorite(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await models.Series_favorite.add(series_id=series_id, user_id=user.id)


@router.delete('', status_code=204)
async def series_remove_from_favorite(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await models.Series_favorite.remove(series_id=series_id, user_id=user.id)