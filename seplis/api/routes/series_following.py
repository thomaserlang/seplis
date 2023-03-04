from fastapi import APIRouter, Security
from ..dependencies import authenticated
from .. import models, schemas, constants

router = APIRouter(prefix='/2/series/{series_id}/following')


@router.get('', response_model=schemas.Series_user_following)
async def following_series(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    return await models.Series_follower.get(series_id=series_id, user_id=user.id)
    

@router.put('', status_code=204)
async def follow_series(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await models.Series_follower.follow(series_id=series_id, user_id=user.id)


@router.delete('', status_code=204)
async def unfollow_series(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await models.Series_follower.unfollow(series_id=series_id, user_id=user.id)