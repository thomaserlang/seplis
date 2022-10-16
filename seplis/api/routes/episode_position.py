from fastapi import Depends, Security, APIRouter, Body
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions


router = APIRouter(prefix='/2/series')


@router.get('/{series_id}/episodes/{episode_number}/position', response_model=schemas.Episode_watched)
async def get_position(
    series_id: int, 
    episode_number: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    ew = await session.scalar(sa.select(models.Episode_watched).where(
        models.Episode_watched.show_id == series_id,
        models.Episode_watched.episode_number == episode_number,
        models.Episode_watched.user_id == user.id,
    ))
    if not ew:
        raise exceptions.Not_found('Episode hasn\'t been watched')
    return schemas.Episode_watched.from_orm(ew)
    

@router.put('/{series_id}/episodes/{episode_number}/position', status_code=204)
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


@router.delete('/{series_id}/episodes/{episode_number}/position', status_code=204)
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