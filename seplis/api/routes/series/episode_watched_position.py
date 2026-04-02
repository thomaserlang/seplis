import sqlalchemy as sa
from fastapi import Body, Depends, Response, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get('/{series_id}/episodes/{episode_number}/watched-position', response_model=schemas.Episode_watched,
            description='''
            **Scope required:** `user:progress`
            ''')
async def get_position(
    series_id: int, 
    episode_number: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    ew = await session.scalar(sa.select(models.MEpisodeWatched).where(
        models.MEpisodeWatched.series_id == series_id,
        models.MEpisodeWatched.episode_number == episode_number,
        models.MEpisodeWatched.user_id == user.id,
    ))
    if not ew:
        return Response(status_code=204)
    return schemas.Episode_watched.model_validate(ew)


@router.put('/{series_id}/episodes/{episode_number}/watched-position', status_code=204,
            description='''
            **Scope required:** `user:progress`
            ''')
async def set_position(
    series_id: int, 
    episode_number: int,
    position: int = Body(..., embed=True, ge=0, le=86400),
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
) -> None:
    await models.MEpisodeWatched.set_position(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
        position=position,
    )
    await session.commit()


@router.delete('/{series_id}/episodes/{episode_number}/watched-position', status_code=204,
            description='''
            **Scope required:** `user:progress`
            ''')
async def delete_position(
    series_id: int, 
    episode_number: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
) -> None:
    await models.MEpisodeWatched.reset_position(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
    )
    await session.commit()