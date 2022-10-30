from fastapi import APIRouter, Security
from ..dependencies import authenticated, get_session, Depends, AsyncSession
from .. import models, schemas, constants

router = APIRouter(prefix='/2/series/{series_id}/following')

@router.get('')
async def following_series(
    series_id: int,
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession = Depends(get_session),
):
    return await models.Series_following.get(series_id=series_id, user_id=user.id, session=session)
    

@router.put('', status_code=204)
async def follow_series(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession = Depends(get_session),
):
    await models.Series_following.follow(series_id=series_id, user_id=user.id, session=session)
    await session.commit()


@router.delete('', status_code=204)
async def unfollow_series(
    series_id: int,    
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession = Depends(get_session),
):
    await models.Series_following.unfollow(series_id=series_id, user_id=user.id, session=session)
    await session.commit()