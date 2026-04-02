import sqlalchemy as sa
from fastapi import Body, Depends, Security
from pydantic import conint

from ... import exceptions, models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get('/{series_id}/episodes/{episode_number}/watched', response_model=schemas.Episode_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def get_watched(
    series_id: conint(ge=1),
    episode_number: conint(ge=1),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    ew = await session.scalar(sa.select(models.MEpisodeWatched).where(
        models.MEpisodeWatched.user_id == user.id,
        models.MEpisodeWatched.series_id == series_id,
        models.MEpisodeWatched.episode_number == episode_number,
    ))
    if ew:
        return schemas.Episode_watched.model_validate(ew)
    return schemas.Episode_watched(episode_number=episode_number)


@router.post('/{series_id}/episodes/{episode_number}/watched', response_model=schemas.Episode_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def watched_increment(
    series_id: conint(ge=1),
    episode_number: conint(ge=1),
    request: dict | None = None,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):  
    data = schemas.Episode_watched_increment.model_validate(request) if request else schemas.Episode_watched_increment()
    await models.MEpisodeWatched.increment(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
        data=data,
    )
    ew = await session.scalar(sa.select(models.MEpisodeWatched).where(
        models.MEpisodeWatched.user_id == user.id,
        models.MEpisodeWatched.series_id == series_id,
        models.MEpisodeWatched.episode_number == episode_number,
    ))
    await session.commit()
    return schemas.Episode_watched.model_validate(ew)


@router.delete('/{series_id}/episodes/{episode_number}/watched', response_model=schemas.Episode_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def watched_decrement(
    series_id: conint(ge=1),
    episode_number: conint(ge=1),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),    
):
    await models.MEpisodeWatched.decrement(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
    )
    ew = await session.scalar(sa.select(models.MEpisodeWatched).where(
        models.MEpisodeWatched.user_id == user.id,
        models.MEpisodeWatched.series_id == series_id,
        models.MEpisodeWatched.episode_number == episode_number,
    ))
    await session.commit()
    if ew:
        return schemas.Episode_watched.model_validate(ew)
    return schemas.Episode_watched(episode_number=episode_number)


@router.post('/{series_id}/episodes/watched-range', status_code=204,
            description='''
            **Scope required:** `user:progress`
            ''')
async def watched_increment_range(
    series_id: conint(ge=1),
    from_episode_number: int = Body(..., embed=True, ge=1),
    to_episode_number: int = Body(..., embed=True, ge=1),
    request: dict | None = None,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
) -> None:  
    data = schemas.Episode_watched_increment.model_validate(request) if request else schemas.Episode_watched_increment()
    if to_episode_number < from_episode_number:
        raise exceptions.API_exception(400, 0, 'to_episode_number must be bigger than from_episode_number')
    for n in range(from_episode_number, to_episode_number+1):
        await models.MEpisodeWatched.increment(
            session=session,
            user_id=user.id,
            series_id=series_id,
            episode_number=n,
            data=data,
        )
    await session.commit()