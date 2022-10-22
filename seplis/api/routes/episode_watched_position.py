from fastapi import Depends, Security, APIRouter, Body, Response
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants


router = APIRouter(prefix='/2/series/{series_id}/episodes/{episode_number}/watched-position')


@router.get('', response_model=schemas.Episode_watched)
async def get_position(
    series_id: int, 
    episode_number: int,
    response: Response,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    ew = await session.scalar(sa.select(models.Episode_watched).where(
        models.Episode_watched.show_id == series_id,
        models.Episode_watched.episode_number == episode_number,
        models.Episode_watched.user_id == user.id,
    ))
    if not ew:
        response.status_code = 204
        return
    return schemas.Episode_watched.from_orm(ew)
    

@router.put('', status_code=204)
async def set_position(
    series_id: int, 
    episode_number: int,
    position: int = Body(..., embed=True, ge=0, le=86400),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    await models.Episode_watched.set_position(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
        position=position,
    )
    await session.commit()


@router.delete('', status_code=204)
async def delete_position(
    series_id: int, 
    episode_number: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    await models.Episode_watched.reset_position(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
    )
    await session.commit()