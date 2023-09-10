from fastapi import Depends, Security, Body, Response
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
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
    ew = await session.scalar(sa.select(models.Episode_watched).where(
        models.Episode_watched.series_id == series_id,
        models.Episode_watched.episode_number == episode_number,
        models.Episode_watched.user_id == user.id,
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
):
    await models.Episode_watched.set_position(
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
):
    await models.Episode_watched.reset_position(
        session=session,
        user_id=user.id,
        series_id=series_id,
        episode_number=episode_number,
    )
    await session.commit()