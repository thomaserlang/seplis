from fastapi import Depends, Security, APIRouter, Body
from pydantic import conint
import sqlalchemy as sa
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions


router = APIRouter(prefix='/2/series')


@router.get('/{series_id}/episodes/{episode_number}/watched', response_model=schemas.Episode_watched)
async def get_watched(
    series_id: conint(ge=1),
    episode_number: conint(ge=1),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    ew = await session.scalar(sa.select(models.Episode_watched).where(
        models.Episode_watched.user_id == user.id,
        models.Episode_watched.series_id == series_id,
        models.Episode_watched.episode_number == episode_number,
    ))
    if ew:
        return schemas.Episode_watched.from_orm(ew)
    else:
        return schemas.Episode_watched(episode_number=episode_number)


@router.post('/{series_id}/episodes/{episode_number}/watched', response_model=schemas.Episode_watched)
async def watched_increment(
    series_id: conint(ge=1),
    episode_number: conint(ge=1),
    request: dict | None = None,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):  
    data = schemas.Episode_watched_increment.parse_obj(request) if request else schemas.Episode_watched_increment()
    await models.Episode_watched.increment(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
        data=data,
    )
    ew = await session.scalar(sa.select(models.Episode_watched).where(
        models.Episode_watched.user_id == user.id,
        models.Episode_watched.series_id == series_id,
        models.Episode_watched.episode_number == episode_number,
    ))
    await session.commit()
    return schemas.Episode_watched.from_orm(ew)


@router.delete('/{series_id}/episodes/{episode_number}/watched', response_model=schemas.Episode_watched)
async def watched_decrement(
    series_id: conint(ge=1),
    episode_number: conint(ge=1),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),    
):
    await models.Episode_watched.decrement(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
    )
    ew = await session.scalar(sa.select(models.Episode_watched).where(
        models.Episode_watched.user_id == user.id,
        models.Episode_watched.series_id == series_id,
        models.Episode_watched.episode_number == episode_number,
    ))
    await session.commit()
    if ew:
        return schemas.Episode_watched.from_orm(ew)
    else:
        return schemas.Episode_watched(episode_number=episode_number)


@router.post('/{series_id}/episodes/watched-range', status_code=204)
async def watched_increment_range(
    series_id: conint(ge=1),
    from_episode_number: int = Body(..., embed=True, ge=1),
    to_episode_number: int = Body(..., embed=True, ge=1),
    request: dict | None = None,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):  
    data = schemas.Episode_watched_increment.parse_obj(request) if request else schemas.Episode_watched_increment()
    if to_episode_number < from_episode_number:
        raise exceptions.API_exception(400, 0, 'to_episode_number must be bigger than from_episode_number')
    for n in range(from_episode_number, to_episode_number+1):
        await models.Episode_watched.increment(
            session=session,
            user_id=user.id,
            series_id=series_id,
            episode_number=n,
            data=data,
        )
    await session.commit()