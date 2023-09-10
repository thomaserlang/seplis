from fastapi import Depends, HTTPException, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_current_user_no_raise, get_expand, get_session, AsyncSession
from ... import models, schemas
from ...expand.episodes import expand_episodes
from .router import router


@router.get('/{series_id}/episodes/{number}', response_model=schemas.Episode)
async def get_episode(
    series_id: int,
    number: int,
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise),
    session: AsyncSession = Depends(get_session),
):
    episode = await session.scalar(sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
    if not episode:
        raise HTTPException(404, 'Unknown episode')
    
    episode = schemas.Episode.model_validate(episode)
    await expand_episodes(episodes=[episode], series_id=series_id, user=user, expand=expand)
    return episode


@router.delete('/{series_id}/episodes/{number}', status_code=204,
            description='''
            **Scope required:** `series:edit`
            ''')
async def delete_episode(
    series_id: int,
    number: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['series:edit']),
):
    await session.execute(sa.delete(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
